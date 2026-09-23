"""フリーチャット。相談しながら文章を詰めていく用。"""

from __future__ import annotations

import streamlit as st

from core import history, prompts
from core.gemini import APIKeyError, create_chat, describe_error, stream_chat
from core.ui import page_header, stream_markdown

STATE_KEY = "chat_messages"


def render() -> None:
    page_header("💬", "フリーチャット", "決まった型のない相談や、生成結果の手直しはこちらで。")

    messages: list[dict] = st.session_state.setdefault(STATE_KEY, [])

    col1, col2 = st.columns([3, 1])
    with col1:
        persona = st.text_input(
            "AIの役割（任意）",
            key="chat_persona",
            placeholder="例: 辛口の編集者として、遠慮なく指摘して",
        )
    with col2:
        st.write("")
        if st.button("🗑 会話をリセット", use_container_width=True, disabled=not messages):
            st.session_state[STATE_KEY] = []
            st.rerun()

    for message in messages:
        with st.chat_message("user" if message["role"] == "user" else "assistant"):
            st.markdown(message["text"])

    user_input = st.chat_input("メッセージを入力（Shift+Enter で改行）")
    if not user_input:
        return

    messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    system = prompts.CHAT_SYSTEM
    if persona.strip():
        system += f"\n\n追加の役割指定: {persona.strip()}"

    with st.chat_message("assistant"):
        try:
            chat = create_chat(system, history=messages[:-1])
            reply = stream_markdown(stream_chat(chat, user_input))
        except APIKeyError as exc:
            st.warning(str(exc))
            messages.pop()
            return
        except Exception as exc:
            st.error(describe_error(exc))
            messages.pop()
            return

    messages.append({"role": "model", "text": reply})

    # 会話は都度保存せず、区切りとして直近のやり取りだけ履歴に残す
    history.add("チャット", user_input[:40], reply, {"往復数": len(messages) // 2})
