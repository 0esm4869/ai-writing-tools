"""AI ライティングスタジオ — Streamlit + Gemini API の個人用ライティングツール。

起動:  streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from core.config import (
    APP_ICON,
    APP_TITLE,
    DEFAULT_MODEL,
    get_env_api_key,
    normalize_api_key,
)
from core.gemini import available_models
from tools import blog, chat, history_view, idea, mail, proofread, rewrite, sns, summarize, translate

PAGES = {
    "✍️ ブログ記事作成": blog.render,
    "📧 メール作成・返信": mail.render,
    "📝 要約": summarize.render,
    "🔍 校正・推敲": proofread.render,
    "🔁 リライト・トーン変換": rewrite.render,
    "🌐 翻訳": translate.render,
    "📣 SNS投稿文": sns.render,
    "💡 アイデア出し": idea.render,
    "💬 フリーチャット": chat.render,
    "🕘 履歴": history_view.render,
}


def sidebar() -> str:
    with st.sidebar:
        st.title(f"{APP_ICON} {APP_TITLE}")
        page = st.radio("ツール", list(PAGES.keys()), label_visibility="collapsed")

        st.divider()
        # モデル一覧の取得にキーが要るので、APIキーの入力を先に描画する。
        api_key_section()

        st.divider()
        model_selector()

        with st.expander("⚙️ 生成の詳細設定"):
            st.slider(
                "創造性 (temperature)",
                0.0,
                2.0,
                0.7,
                step=0.1,
                key="temperature",
                help="低いほど堅実・一貫的、高いほど多様で大胆な表現になります。",
            )
            st.checkbox(
                "熟考モード",
                key="thinking",
                help="生成前に思考を挟み、長文や複雑な指示の精度が上がります。その分遅くなります。",
            )
            st.text_input(
                "モデルIDを直接指定（任意）",
                key="model_override",
                placeholder="例: gemini-3.6-pro",
                help="一覧に出ないモデルを使いたいときに入力します。空欄なら上の選択が使われます。",
            )

    return page


def model_selector() -> None:
    """選択肢はAPIから取得する。モデル名は提供終了で変わるため固定できない。"""
    models = available_models()
    ids = list(models)

    # 一覧が入れ替わって選択中のIDが消えると selectbox が壊れるので捨てる。
    if st.session_state.get("model_select") not in ids:
        st.session_state.pop("model_select", None)

    current = st.session_state.get("model")
    default_index = ids.index(current) if current in ids else 0
    chosen = st.selectbox("モデル", ids, index=default_index, key="model_select")

    override = (st.session_state.get("model_override") or "").strip()
    st.session_state["model"] = override or chosen

    if override:
        st.caption(f"モデルIDの直接指定を使用中: `{override}`")
    elif models.get(chosen):
        st.caption(models[chosen])


def entered_api_key() -> str:
    """入力欄の現在値を正規化して返す。描画前でも参照できる。"""
    raw = st.session_state.get("api_key_input") or ""
    return normalize_api_key(raw)


def api_key_field() -> None:
    """キー入力欄。値は session_state["api_key"] に書き写して保持する。"""
    st.text_input(
        "Gemini API キー",
        type="password",
        key="api_key_input",
        help="https://aistudio.google.com/apikey で取得できます。",
    )
    key = entered_api_key()
    st.session_state["api_key"] = key
    if key and not key.isascii():
        st.error(
            "キーに全角文字が含まれています。IME を半角にして入力し直すか、"
            "Google AI Studio からコピーし直してください。",
            icon="⚠️",
        )


def api_key_section() -> None:
    """APIキーの状態表示と入力欄。

    入力欄は「設定済み」でも expander の中に描画し続ける。Streamlit は画面から
    消えたウィジェットの値を破棄するため、入力欄を出し分けるとキーが消える。
    """
    if get_env_api_key():
        st.success("API キー: 設定済み（.env から読み込み）", icon="✅")
        return

    # 判定にはウィジェット自身の状態を使う。session_state["api_key"] は
    # api_key_field() が描画されて初めて書き込まれるため、入力直後の実行では
    # まだ古い値のままで、「設定済み」表示が1テンポ遅れる。
    key = entered_api_key()
    if key and key.isascii():
        st.success("API キー: 設定済み", icon="✅")
        with st.expander("キーを変更する"):
            api_key_field()
    else:
        api_key_field()
        st.caption(".env に `GEMINI_API_KEY=...` を書いておくと、毎回の入力が不要になります。")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="wide")
    page = sidebar()
    PAGES[page]()


if __name__ == "__main__":
    main()
