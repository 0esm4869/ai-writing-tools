"""設定まわり（APIキーの取得、モデル一覧、生成パラメータ）。"""

from __future__ import annotations

import os
import unicodedata
from dataclasses import dataclass

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

APP_TITLE = "AI ライティングスタジオ"
APP_ICON = "✍️"

# 実際の選択肢は core.gemini.available_models() が API から取得する。
# ここはキー未設定・オフラインなど、一覧を取得できないときの候補。
FALLBACK_MODELS: dict[str, str] = {
    "gemini-3.6-flash": "バランス型。日常のライティング向け",
    "gemini-2.5-flash": "旧世代。新規ユーザーには提供されていない場合がある",
}
DEFAULT_MODEL = "gemini-3.6-flash"


@dataclass(frozen=True)
class GenSettings:
    """生成時のパラメータ。サイドバーの値をまとめて持ち回る。"""

    model: str = DEFAULT_MODEL
    temperature: float = 0.7
    thinking: bool = False


def normalize_api_key(raw: str) -> str:
    """入力されたキーを整える。

    APIキーは HTTP ヘッダーに載るため ASCII でなければならない。IME が全角
    モードのまま入力された `ＡＢＣ` のようなキーは NFKC 正規化で半角に戻せる。
    貼り付け時に紛れ込む空白・改行・引用符もここで落とす。
    """
    key = unicodedata.normalize("NFKC", raw)
    key = "".join(key.split())
    return key.strip("\"'")


def get_env_api_key() -> str | None:
    """環境変数(.env) → st.secrets の順で APIキーを探す。"""
    for name in ("GEMINI_API_KEY", "GOOGLE_API_KEY"):
        value = os.getenv(name)
        if value:
            return value.strip()

    try:  # secrets.toml が無い環境では例外になるので握りつぶす
        return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        return None


def get_api_key() -> str | None:
    """サイドバー入力 → 環境変数 の順で APIキーを探す。

    session_state["api_key"] はウィジェットの key ではなく、サイドバーが値を
    書き写すための通常のキー。ウィジェットの key をそのまま参照すると、
    入力欄を画面から消した瞬間に Streamlit が値を破棄してしまう。
    """
    key = st.session_state.get("api_key")
    if key:
        return key
    env_key = get_env_api_key()
    return normalize_api_key(env_key) if env_key else None


def current_settings() -> GenSettings:
    """サイドバーで選択中の設定を返す。"""
    return GenSettings(
        model=st.session_state.get("model") or DEFAULT_MODEL,
        temperature=float(st.session_state.get("temperature", 0.7)),
        thinking=bool(st.session_state.get("thinking", False)),
    )
