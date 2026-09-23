"""校正・推敲ツール。"""

from __future__ import annotations

import streamlit as st

from core import prompts, ui

LEVELS = {
    "誤字脱字のみ": "誤字・脱字・変換ミス・明らかな文法誤りだけを直す。表現は変えない。",
    "標準（誤字＋表記ゆれ＋読みやすさ）": "誤字脱字、表記ゆれ、助詞の誤り、冗長な言い回し、一文の長さを整える。",
    "しっかり推敲（構成・論理も見る）": "誤字脱字に加え、論理の飛躍、重複、順序の不自然さ、曖昧な主語も指摘して整える。",
    "ビジネス文書チェック": "誤字脱字に加え、敬語の誤り・二重敬語・失礼な表現・曖昧な依頼を重点的に直す。",
}


def render() -> None:
    ui.page_header("🔍", "校正・推敲", "誤字脱字や読みにくさを直し、どこをなぜ直したかも表示します。")

    text = ui.text_input_area("proof_text", label="校正したい文章", height=280)

    col1, col2 = st.columns([2, 1])
    with col1:
        level_label = st.selectbox("チェックの強さ", list(LEVELS.keys()), index=1, key="proof_level")
    with col2:
        report = st.checkbox("指摘一覧を出す", value=True, key="proof_report")

    run = st.button("🔍 校正する", type="primary", use_container_width=True, disabled=not text.strip())

    ui.generate(
        state_key="proof_result",
        run=run,
        prompt=prompts.proofread_prompt(text, LEVELS[level_label], report),
        system_instruction=prompts.PROOFREAD_SYSTEM,
        tool="校正・推敲",
        title=text[:40],
        meta={"レベル": level_label},
    )
