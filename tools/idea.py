"""アイデア出し・タイトル案ツール。"""

from __future__ import annotations

import streamlit as st

from core import prompts, ui

KINDS = [
    "ブログ記事のタイトル案",
    "ブログ記事のネタ（テーマ）案",
    "キャッチコピー",
    "メールの件名案",
    "動画・配信のタイトル案",
    "プレゼンの構成案",
    "商品・サービスの説明文案",
]


def render() -> None:
    ui.page_header("💡", "アイデア出し", "タイトル・切り口に詰まったときに、角度の違う案を並べます。")

    kind = st.selectbox("出したいもの", KINDS, key="idea_kind")
    topic = st.text_area(
        "テーマ・前提", key="idea_topic", height=120, placeholder="例: 在宅ワークの集中力を上げる方法についての記事"
    )

    col1, col2 = st.columns(2)
    with col1:
        audience = st.text_input("想定読者", key="idea_audience", value="一般の社会人")
    with col2:
        count = st.number_input("案の数", 3, 30, 10, key="idea_count")

    extra = st.text_input("条件・制約（任意）", key="idea_extra", placeholder="例: 30字以内 / 数字を入れる / 煽らない")

    run = st.button("💡 案を出す", type="primary", use_container_width=True, disabled=not topic.strip())

    ui.generate(
        state_key="idea_result",
        run=run,
        prompt=prompts.idea_prompt(kind, topic, audience, int(count), extra),
        system_instruction=prompts.IDEA_SYSTEM,
        tool="アイデア出し",
        title=f"{kind}: {topic[:30]}",
        meta={"種類": kind, "数": int(count)},
    )
