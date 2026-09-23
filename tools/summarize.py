"""文章の要約ツール。"""

from __future__ import annotations

import streamlit as st

from core import prompts, ui

STYLES = {
    "箇条書き（要点のみ）": "重要な論点を箇条書きで列挙する。各項目は1〜2文。",
    "3行まとめ": "最も重要な内容を3行にまとめる。1行は40字程度。",
    "文章（段落形式）": "自然な段落の文章として要約する。",
    "議事録スタイル": "「決定事項」「議論の要点」「ToDo（担当者・期限があれば明記）」の3見出しで整理する。",
    "1行タイトル": "内容を表す見出しを1行だけ作る。",
    "構造化（見出し＋要点）": "内容を数個のトピックに分け、見出しごとに要点を箇条書きする。",
}

LENGTHS = ["超短め（原文の5%程度）", "短め（原文の10%程度）", "標準（原文の20%程度）", "詳しめ（原文の30%程度）"]


def render() -> None:
    ui.page_header("📝", "要約", "長文・議事録・記事などを、目的に合わせた形で圧縮します。")

    text = ui.text_input_area("sum_text", label="要約したい文章", height=280)

    col1, col2 = st.columns(2)
    with col1:
        style_label = st.selectbox("要約の形式", list(STYLES.keys()), key="sum_style")
    with col2:
        length = st.selectbox("分量", LENGTHS, index=2, key="sum_length")

    purpose = st.text_input(
        "用途・読み手（任意）", key="sum_purpose", placeholder="例: 上司への報告用 / 自分の復習用"
    )

    run = st.button("📝 要約する", type="primary", use_container_width=True, disabled=not text.strip())

    ui.generate(
        state_key="sum_result",
        run=run,
        prompt=prompts.summary_prompt(text, STYLES[style_label], length, purpose),
        system_instruction=prompts.SUMMARY_SYSTEM,
        tool="要約",
        title=text[:40],
        meta={"形式": style_label, "分量": length},
    )
