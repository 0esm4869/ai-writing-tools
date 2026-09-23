"""Gemini API のラッパー。すべてストリーミングでテキストを返す。"""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import replace

import streamlit as st
from google import genai
from google.genai import types

from core.config import (
    FALLBACK_MODELS,
    GenSettings,
    current_settings,
    get_api_key,
)


class APIKeyError(RuntimeError):
    """APIキーが無い、または使えない形式。ui.generate が警告表示に変換する。"""


class MissingAPIKeyError(APIKeyError):
    pass


class InvalidAPIKeyError(APIKeyError):
    pass


@st.cache_resource(show_spinner=False)
def _client(api_key: str) -> genai.Client:
    """APIキーごとにクライアントを使い回す。"""
    return genai.Client(api_key=api_key)


def get_client() -> genai.Client:
    api_key = get_api_key()
    if not api_key:
        raise MissingAPIKeyError(
            "Gemini API キーが設定されていません。サイドバーから入力するか、"
            ".env に GEMINI_API_KEY を設定してください。"
        )
    if not api_key.isascii():
        # キーは HTTP ヘッダーに載るため、全角文字が残っていると httpx が
        # UnicodeEncodeError を投げる。手前で止めて理由を伝える。
        raise InvalidAPIKeyError(
            "API キーに全角文字など、半角英数字以外の文字が含まれています。"
            "Google AI Studio のキーをもう一度コピーし直して貼り付けてください"
            "（手入力する場合は、IME を半角モードにしてください）。"
        )
    return _client(api_key)


@st.cache_data(ttl=3600, show_spinner=False)
def _fetch_models(api_key: str) -> dict[str, str]:
    """APIが返すモデル一覧。api_key は cache のキーを分けるために受け取る。"""
    found: dict[str, str] = {}
    for model in _client(api_key).models.list():
        name = (model.name or "").split("/")[-1]
        if not name.startswith("gemini-"):
            continue
        actions = model.supported_actions
        if actions and "generateContent" not in actions:
            continue
        found[name] = (model.description or model.display_name or "").strip()
    return dict(sorted(found.items(), reverse=True))


def available_models() -> dict[str, str]:
    """選択できるモデル {ID: 説明}。

    モデル名は提供終了などで変わるため、APIから取得したものを正とする。
    キー未設定・オフライン・キー不正のときは静的な候補にフォールバックする。
    """
    api_key = get_api_key()
    if api_key and api_key.isascii():
        try:
            models = _fetch_models(api_key)
            if models:
                return models
        except Exception:
            pass
    return dict(FALLBACK_MODELS)


def build_config(
    settings: GenSettings,
    system_instruction: str | None = None,
    max_output_tokens: int | None = None,
) -> types.GenerateContentConfig:
    # 許容される thinking の値はモデルごとに違う。オフのときは何も指定せず
    # モデルの既定に任せ、オンのときだけ自動調整(-1)を要求する。
    thinking_config = types.ThinkingConfig(thinking_budget=-1) if settings.thinking else None

    return types.GenerateContentConfig(
        system_instruction=system_instruction,
        temperature=settings.temperature,
        max_output_tokens=max_output_tokens,
        thinking_config=thinking_config,
    )


def stream_text(
    prompt: str,
    system_instruction: str | None = None,
    settings: GenSettings | None = None,
    max_output_tokens: int | None = None,
) -> Iterator[str]:
    """プロンプトを投げ、生成されたテキストを逐次 yield する。"""
    settings = settings or current_settings()
    client = get_client()

    def run(active: GenSettings) -> Iterator[str]:
        stream = client.models.generate_content_stream(
            model=active.model,
            contents=prompt,
            config=build_config(active, system_instruction, max_output_tokens),
        )
        for chunk in stream:
            text = getattr(chunk, "text", None)
            if text:
                yield text

    started = False
    try:
        for text in run(settings):
            started = True
            yield text
    except Exception as exc:
        # 熟考モードを受け付けないモデルがある。まだ何も出力していなければ
        # thinking 指定を外してやり直す。
        if started or not settings.thinking or "thinking" not in str(exc).lower():
            raise
        yield from run(replace(settings, thinking=False))


def create_chat(system_instruction: str, history: list[dict] | None = None):
    """チャット用セッションを作る。history は {role, text} のリスト。"""
    settings = current_settings()
    client = get_client()

    contents = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["text"])],
        )
        for m in (history or [])
    ]
    return client.chats.create(
        model=settings.model,
        config=build_config(settings, system_instruction),
        history=contents,
    )


def stream_chat(chat, message: str) -> Iterator[str]:
    for chunk in chat.send_message_stream(message):
        text = getattr(chunk, "text", None)
        if text:
            yield text


def count_tokens(text: str) -> int | None:
    """入力テキストの概算トークン数。失敗したら None。"""
    try:
        result = get_client().models.count_tokens(
            model=current_settings().model, contents=text
        )
        return result.total_tokens
    except Exception:
        return None
