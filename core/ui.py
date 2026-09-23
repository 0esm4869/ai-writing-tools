"""各ツール画面で共通して使う UI 部品。"""

from __future__ import annotations

import re
from datetime import datetime

import streamlit as st

from core import history
from core.gemini import APIKeyError, describe_error, stream_text


def page_header(icon: str, title: str, description: str) -> None:
    st.subheader(f"{icon} {title}")
    st.caption(description)


def text_input_area(
    key: str,
    label: str = "対象のテキスト",
    height: int = 260,
    placeholder: str = "ここに貼り付け、またはファイルをアップロードしてください。",
) -> str:
    """テキストエリア＋.txt/.md アップロードの組み合わせ入力。"""
    uploaded = st.file_uploader(
        "ファイルから読み込む（任意・.txt / .md）",
        type=["txt", "md"],
        key=f"{key}_file",
    )
    if uploaded is not None:
        try:
            content = uploaded.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            content = uploaded.getvalue().decode("shift_jis", errors="replace")
        st.session_state[key] = content

    text = st.text_area(label, key=key, height=height, placeholder=placeholder)
    if text:
        st.caption(f"{len(text):,} 文字")
    return text or ""


def _slugify(text: str) -> str:
    cleaned = re.sub(r"[\\/:*?\"<>|\s]+", "_", text.strip())
    return (cleaned[:40] or "output").strip("_")


def result_actions(result: str, tool: str, title: str, key: str = "") -> None:
    """生成結果に対するコピー／ダウンロード／再利用の操作群。"""
    col1, col2, col3 = st.columns([1, 1, 2])
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    with col1:
        st.download_button(
            "⬇️ .md で保存",
            data=result,
            file_name=f"{_slugify(title)}_{stamp}.md",
            mime="text/markdown",
            use_container_width=True,
            key=f"dl_md_{key or tool}_{stamp}",
        )
    with col2:
        st.download_button(
            "⬇️ .txt で保存",
            data=result,
            file_name=f"{_slugify(title)}_{stamp}.txt",
            mime="text/plain",
            use_container_width=True,
            key=f"dl_txt_{key or tool}_{stamp}",
        )
    with col3:
        st.caption(f"{len(result):,} 文字 / {tool}")

    with st.expander("📋 コピー用（右上のアイコンでコピー）"):
        st.code(result, language="markdown")


def stream_markdown(chunks) -> str:
    """チャンクを順に追記しながら Markdown 表示し、全文を返す。

    st.write_stream は入力を is_dataframe_like() で型判定するため pandas を
    読み込む。Windows の Smart App Control が pandas の .pyd を弾く環境では
    それだけで生成が落ちるので、自前で st.empty() に描き足していく。
    """
    placeholder = st.empty()
    parts: list[str] = []
    for chunk in chunks:
        parts.append(chunk)
        placeholder.markdown("".join(parts) + "▌")
    text = "".join(parts)
    placeholder.markdown(text)
    return text


def generate(
    *,
    state_key: str,
    run: bool,
    prompt: str,
    system_instruction: str,
    tool: str,
    title: str,
    meta: dict | None = None,
    as_markdown: bool = True,
) -> str | None:
    """ストリーミング生成 → 表示 → 履歴保存 → 操作ボタン、までを一括で行う。

    run=True の実行時はストリーム表示し、それ以外は直近の結果を再描画する。
    """
    if run:
        st.divider()
        try:
            with st.spinner("生成中…"):
                result = stream_markdown(stream_text(prompt, system_instruction))
        except APIKeyError as exc:
            st.warning(str(exc))
            return None
        except Exception as exc:  # APIエラーはそのまま見せた方がデバッグしやすい
            st.error(describe_error(exc))
            return None

        st.session_state[state_key] = result
        history.add(tool, title, result, meta)
        result_actions(result, tool, title)
        return result

    result = st.session_state.get(state_key)
    if result:
        st.divider()
        if as_markdown:
            st.markdown(result)
        else:
            st.text(result)
        result_actions(result, tool, title)
    return result
