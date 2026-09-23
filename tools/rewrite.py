"""リライト・トーン変換ツール。"""

from __future__ import annotations

import streamlit as st

from core import prompts, ui

TONES = [
    "ビジネス文書として硬く",
    "やわらかく親しみやすく",
    "です・ます調に統一",
    "だ・である調に統一",
    "専門知識のない人にもわかるやさしい言葉で",
    "説得力のあるセールスライティング調",
    "感情を抑えた客観的な説明",
    "カジュアルな話し言葉",
]

LENGTH_MODES = [
    "元の分量を保つ",
    "半分程度に圧縮する",
    "3割ほど短くする",
    "1.5倍程度に膨らませる（具体例を足す）",
    "箇条書きに変換する",
]


def render() -> None:
    ui.page_header("🔁", "リライト・トーン変換", "内容はそのままに、文体・分量だけを変えます。")

    text = ui.text_input_area("rw_text", label="書き換えたい文章", height=260)

    col1, col2 = st.columns(2)
    with col1:
        tone = st.selectbox("変換後のトーン", TONES, key="rw_tone")
    with col2:
        length_mode = st.selectbox("分量", LENGTH_MODES, key="rw_length")

    extra = st.text_input("追加の指示（任意）", key="rw_extra", placeholder="例: 専門用語には短い説明を添える")

    run = st.button("🔁 書き換える", type="primary", use_container_width=True, disabled=not text.strip())

    ui.generate(
        state_key="rw_result",
        run=run,
        prompt=prompts.rewrite_prompt(text, tone, length_mode, extra),
        system_instruction=prompts.REWRITE_SYSTEM,
        tool="リライト",
        title=text[:40],
        meta={"トーン": tone, "分量": length_mode},
    )
