"""翻訳ツール。"""

from __future__ import annotations

import streamlit as st

from core import prompts, ui

LANGUAGES = ["英語", "日本語", "中国語（簡体字）", "中国語（繁体字）", "韓国語", "フランス語", "ドイツ語", "スペイン語", "ポルトガル語", "イタリア語", "ベトナム語", "タイ語"]
TONES = ["原文のトーンに合わせる", "ビジネス・フォーマル", "カジュアル・口語", "技術文書・マニュアル調", "マーケティング・訴求重視"]


def render() -> None:
    ui.page_header("🌐", "翻訳", "直訳ではなく、読み手に自然な訳文を作ります。")

    text = ui.text_input_area("tr_text", label="翻訳したい文章", height=240)

    col1, col2 = st.columns(2)
    with col1:
        target = st.selectbox("翻訳先の言語", LANGUAGES, key="tr_target")
    with col2:
        tone = st.selectbox("文体", TONES, key="tr_tone")

    with st.expander("詳細設定"):
        glossary = st.text_area(
            "用語集（任意・1行1組で「原語 = 訳語」）",
            key="tr_glossary",
            height=100,
            placeholder="例:\n案件 = project\n稟議 = internal approval",
        )
        notes = st.checkbox("訳注（訳し分けの補足）をつける", key="tr_notes")

    run = st.button("🌐 翻訳する", type="primary", use_container_width=True, disabled=not text.strip())

    ui.generate(
        state_key="tr_result",
        run=run,
        prompt=prompts.translate_prompt(text, target, tone, glossary, notes),
        system_instruction=prompts.TRANSLATE_SYSTEM,
        tool="翻訳",
        title=f"{target}訳: {text[:30]}",
        meta={"言語": target, "文体": tone},
    )
