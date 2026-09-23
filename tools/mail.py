"""メールの返信案・新規作成ツール。"""

from __future__ import annotations

import streamlit as st

from core import prompts, ui

RELATIONSHIPS = ["社外の取引先", "社外（初めての相手）", "社内の上司", "社内の同僚・部下", "顧客・お客様", "友人・知人"]
TONES = ["丁寧でフォーマル", "丁寧だが簡潔", "やわらかく親しみやすい", "毅然と、はっきり断る", "謝罪・お詫び", "カジュアル"]


def render() -> None:
    ui.page_header("📧", "メール作成・返信", "受信メールを貼り付けるだけで、そのまま送れる文面を作ります。")

    mode = st.radio(
        "モード", ["返信", "新規作成"], key="mail_mode", horizontal=True, label_visibility="collapsed"
    )

    received = ""
    if mode == "返信":
        received = st.text_area(
            "受信したメール本文", key="mail_received", height=200, placeholder="返信したいメールを貼り付けてください。"
        )

    intent = st.text_area(
        "伝えたいこと・用件（箇条書きでOK）",
        key="mail_intent",
        height=110,
        placeholder="例:\n・打ち合わせは来週火曜の14時希望\n・資料は前日までに送る\n・日程が合わなければ水曜も可",
    )

    col1, col2 = st.columns(2)
    with col1:
        relationship = st.selectbox("相手との関係", RELATIONSHIPS, key="mail_rel")
    with col2:
        tone = st.selectbox("トーン", TONES, key="mail_tone")

    with st.expander("詳細設定"):
        sender = st.text_input("差出人・署名（任意）", key="mail_sender", placeholder="例: 株式会社◯◯ 山田太郎")
        extra = st.text_area("その他の指示（任意）", key="mail_extra", height=80)

    required_ok = bool(intent) and (mode == "新規作成" or bool(received))
    run = st.button("✉️ 文面を作る", type="primary", use_container_width=True, disabled=not required_ok)
    if not required_ok:
        st.caption("受信メール（返信モードのみ）と用件を入力すると生成できます。")

    ui.generate(
        state_key="mail_result",
        run=run,
        prompt=prompts.mail_prompt(mode, received, intent, relationship, tone, sender, extra),
        system_instruction=prompts.MAIL_SYSTEM,
        tool=f"メール（{mode}）",
        title=intent[:40] if intent else "メール",
        meta={"相手": relationship, "トーン": tone},
    )
