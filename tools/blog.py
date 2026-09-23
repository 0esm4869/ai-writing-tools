"""ブログ記事の構成案・本文を書くツール。"""

from __future__ import annotations

import streamlit as st

from core import prompts, ui

TONES = [
    "です・ます調（親しみやすい）",
    "です・ます調（丁寧・フォーマル）",
    "だ・である調（硬め・解説向き）",
    "カジュアルな語りかけ",
    "専門家として淡々と",
]


def render() -> None:
    ui.page_header(
        "✍️", "ブログ記事作成", "テーマから構成案と本文を生成します。構成を先に作ると精度が上がります。"
    )

    topic = st.text_input(
        "テーマ・タイトル案", key="blog_topic", placeholder="例: 在宅ワークの集中力を上げる環境づくり"
    )

    col1, col2 = st.columns(2)
    with col1:
        audience = st.text_input(
            "想定読者", key="blog_audience", value="在宅ワークを始めたばかりの会社員"
        )
        tone = st.selectbox("文体・トーン", TONES, key="blog_tone")
    with col2:
        keywords = st.text_input(
            "キーワード（カンマ区切り・任意）", key="blog_keywords", placeholder="集中力, デスク環境, 習慣"
        )
        length = st.slider("目標文字数", 800, 8000, 2500, step=200, key="blog_length")

    with st.expander("詳細設定"):
        structure = st.text_area(
            "構成の指定（任意・見出しを貼り付けると、その構成で書きます）",
            key="blog_structure",
            height=140,
        )
        extra = st.text_area("その他の要望（任意）", key="blog_extra", height=80)

    col_a, col_b = st.columns(2)
    with col_a:
        run_outline = st.button(
            "🗂 構成案をつくる", use_container_width=True, disabled=not topic
        )
    with col_b:
        run_article = st.button(
            "📝 本文を書く", type="primary", use_container_width=True, disabled=not topic
        )

    if run_outline:
        st.session_state.pop("blog_result", None)
        ui.generate(
            state_key="blog_outline_result",
            run=True,
            prompt=prompts.blog_outline_prompt(topic, keywords, audience),
            system_instruction=prompts.BLOG_SYSTEM,
            tool="ブログ構成案",
            title=topic,
        )
        st.info("気に入った構成を「詳細設定 > 構成の指定」に貼り付けて本文を書くと、狙い通りの記事になります。")
        return

    if run_article:
        st.session_state.pop("blog_outline_result", None)

    ui.generate(
        state_key="blog_result",
        run=run_article,
        prompt=prompts.blog_prompt(topic, keywords, audience, tone, length, structure, extra),
        system_instruction=prompts.BLOG_SYSTEM,
        tool="ブログ記事",
        title=topic,
        meta={"文字数指定": length, "読者": audience},
    )

    if not run_article and st.session_state.get("blog_outline_result"):
        ui.generate(
            state_key="blog_outline_result",
            run=False,
            prompt="",
            system_instruction="",
            tool="ブログ構成案",
            title=topic,
        )
