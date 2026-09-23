"""SNS投稿文の作成ツール。"""

from __future__ import annotations

import streamlit as st

from core import prompts, ui

PLATFORMS = {
    "X（旧Twitter）": "140字以内（日本語）。改行を使って読みやすく",
    "Instagram": "キャプションとして200〜400字程度",
    "LinkedIn": "400〜800字程度。実績や学びを中心に",
    "Facebook": "200〜400字程度",
    "note の告知文": "150字程度",
    "YouTube の概要欄": "300〜600字程度",
}
TONES = ["丁寧・信頼感重視", "カジュアル・フランク", "熱量高め・勢いよく", "淡々と情報だけ", "共感を誘う語り"]


def render() -> None:
    ui.page_header("📣", "SNS投稿文", "同じ内容を複数パターンで出すので、良い方を選べます。")

    platform = st.selectbox("プラットフォーム", list(PLATFORMS.keys()), key="sns_platform")

    topic = st.text_area(
        "投稿したい内容（元ネタ・URL・記事本文の貼り付けでもOK）",
        key="sns_topic",
        height=160,
        placeholder="例: ブログを更新しました。在宅ワークの集中力を上げるデスク環境の作り方について書いています。",
    )

    col1, col2, col3 = st.columns(3)
    with col1:
        tone = st.selectbox("トーン", TONES, key="sns_tone")
    with col2:
        count = st.number_input("案の数", 1, 6, 3, key="sns_count")
    with col3:
        hashtags = st.checkbox("ハッシュタグ", value=True, key="sns_tags")

    run = st.button("📣 投稿文を作る", type="primary", use_container_width=True, disabled=not topic.strip())

    ui.generate(
        state_key="sns_result",
        run=run,
        prompt=prompts.sns_prompt(platform, topic, tone, int(count), hashtags, PLATFORMS[platform]),
        system_instruction=prompts.SNS_SYSTEM,
        tool=f"SNS投稿（{platform}）",
        title=topic[:40],
        meta={"媒体": platform, "案の数": int(count)},
    )
