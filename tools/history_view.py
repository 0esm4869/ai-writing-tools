"""生成履歴の閲覧・削除。"""

from __future__ import annotations

import streamlit as st

from core import history
from core.ui import page_header, result_actions


def render() -> None:
    page_header("🕘", "履歴", "生成した結果はローカルの data/history.json に保存されます。")

    items = history.load()
    if not items:
        st.info("まだ履歴はありません。")
        return

    tools = sorted({item["tool"] for item in items})
    col1, col2 = st.columns([2, 1])
    with col1:
        selected = st.multiselect("ツールで絞り込み", tools, key="hist_filter")
    with col2:
        keyword = st.text_input("キーワード検索", key="hist_keyword")

    filtered = [
        item
        for item in items
        if (not selected or item["tool"] in selected)
        and (not keyword or keyword.lower() in (item["title"] + item["output"]).lower())
    ]
    st.caption(f"{len(filtered)} / {len(items)} 件")

    for item in filtered[:50]:
        label = f"{item['created_at'].replace('T', ' ')}  |  {item['tool']}  |  {item['title']}"
        with st.expander(label):
            if item.get("meta"):
                st.caption(" / ".join(f"{k}: {v}" for k, v in item["meta"].items()))
            st.markdown(item["output"])
            result_actions(item["output"], item["tool"], item["title"], key=item["id"])
            if st.button("🗑 この履歴を削除", key=f"del_{item['id']}"):
                history.delete(item["id"])
                st.rerun()

    st.divider()
    with st.expander("⚠️ 履歴をすべて削除"):
        if st.button("すべて削除する", type="primary"):
            history.clear()
            st.rerun()
