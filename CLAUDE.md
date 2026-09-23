# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

個人用のAIライティングツール集。Streamlit + Gemini API（`google-genai` SDK）。
**データベースも認証も意図的に持たない。** 状態は `st.session_state`（セッション中のみ）と
`data/history.json`（ローカル永続化）の2つだけ。この方針を変える提案はしないこと。

UIの表示文言・プロンプトはすべて日本語。コード内のコメントとdocstringも日本語で統一されている。

## Commands

```bash
# 起動（Windowsはダブルクリックでも可）
run_app.bat
# または
.venv/Scripts/python.exe -m streamlit run app.py

# 全10画面のレンダリング確認（APIキー不要・ボタンは押さないのでAPI呼び出しは発生しない）
PYTHONIOENCODING=utf-8 ./.venv/Scripts/python.exe -c "
import sys, os
sys.path.insert(0, os.getcwd())
from streamlit.testing.v1 import AppTest
app = os.path.join(os.getcwd(), 'app.py')
bad = 0
for page in AppTest.from_file(app).run().sidebar.radio[0].options:
    at = AppTest.from_file(app, default_timeout=30).run()
    at.sidebar.radio[0].set_value(page).run()
    bad += bool(at.exception)
    print(page, 'FAIL' if at.exception else 'OK')
sys.exit(bad)
" 2>&1 | grep -v ScriptRunContext
```

自動テストはこのスモークチェックのみ。lint / formatter の設定はない。

## Architecture

### 生成処理は `core/ui.py` の `generate()` に一本化されている

チャット以外の8ツールは、入力ウィジェットを並べてプロンプト文字列を組み立て、
最後に `ui.generate()` を1回呼ぶだけ。ストリーミング表示・エラー処理・履歴保存・
ダウンロードボタンはすべてこの関数の中にある。**ツール側に生成ロジックを書かないこと。**

`generate()` は `run`（ボタンが押されたか）で2つの経路に分かれる:

- `run=True` → `stream_markdown()` でストリーム表示 → `session_state[state_key]` に保存 → 履歴に追記
- `run=False` → `session_state[state_key]` から前回結果を再描画

Streamlitはウィジェット操作のたびにスクリプト全体を再実行するため、この使い分けが無いと
スライダーを動かしただけで再生成が走る。新しいツールを追加するときも必ずこの形にする。

### 生成パラメータは session_state 経由の暗黙のグローバル

`app.py` のサイドバーが `st.session_state` に `model` / `temperature` / `thinking` を書き込み、
`config.current_settings()` がそれを読んで `GenSettings` を組み立てる。引数として渡ってこないので、
サイドバーのウィジェットの `key=` を変えると生成設定が黙って壊れる。

### レイヤー構成

```
app.py         PAGES dict（表示名 → render関数）とサイドバー。ツール追加はここに1行足す
core/config.py APIキー解決、モデル一覧、GenSettings
core/gemini.py google-genai のラッパー。stream_text() / create_chat() / stream_chat()
core/prompts.py 全ツールのシステムプロンプトとプロンプト組み立て関数
core/ui.py     generate() / stream_markdown() / text_input_area() / result_actions()
core/history.py data/history.json への読み書き
tools/*.py     1ツール1ファイル。render() を公開するだけ
```

**出力の質に関する変更は `core/prompts.py` だけで完結する。** 全プロンプトが
`BASE_RULES`（前置き禁止・捏造禁止・AI的言い回しの回避）を共有している。

新しいツールは `tools/` に `render()` を持つファイルを作り、`app.py` の `PAGES` に登録する。
選択肢の増減は各 `tools/*.py` 冒頭の定数（`TONES`, `STYLES` など）で済むことが多い。

### APIキーの解決順

`session_state["api_key"]`（サイドバー入力）→ `get_env_api_key()`（環境変数
`GEMINI_API_KEY` / `GOOGLE_API_KEY` → `st.secrets`）。キーが無い場合は
`MissingAPIKeyError` が送出され、`ui.generate()` が `st.warning` に変換するので、
呼び出し側で捕捉する必要はない。

`session_state["api_key"]` は**ウィジェットの key ではない**。入力欄の key は
`api_key_input` で、`app.py` の `api_key_field()` がその値を `api_key` に書き写している。
この二段構えは Streamlit の仕様への対処なので崩さないこと（下記）。

## 注意点

- **`gemini-2.5-pro` は thinking をオフにできない。** `GenSettings.supports_thinking_off` で
  判定し、pro のときは `ThinkingConfig` 自体を渡さない。この分岐を外すとAPIエラーになる。
- **`run_app.bat` は Shift-JIS(cp932) + CRLF で保存すること。** cmd.exe はバッチファイルを
  OSのコードページで読むため、UTF-8で保存すると日本語行のパースに失敗して
  「'...' is not recognized as an internal or external command」になる。編集時は
  `open(..., 'wb').write(text.replace('\n','\r\n').encode('cp932'))` で書き戻す。
- **`.streamlit/config.toml` の `showEmailPrompt = false` は消さないこと。** これが無いと
  初回起動時にメールアドレス入力待ちでサーバーが起動しない。
- **モデルIDをコードに固定しないこと。** Google は提供終了したモデルに 404 を返す
  （`gemini-2.5-flash` が実際にこれで使えなくなった）。選択肢は
  `gemini.available_models()` が `client.models.list()` から取得する。`config.FALLBACK_MODELS`
  はキー未設定・オフライン時の候補にすぎず、正ではない。サイドバーの
  「モデルIDを直接指定」（`model_override`）が一覧に頼らない逃げ道。
- **thinking の許容値はモデルごとに異なる。** 熟考モードOFFでは `thinking_config` を
  一切渡さずモデルの既定に任せる（`thinking_budget=0` を拒否するモデルがあるため）。
  ONのときだけ `thinking_budget=-1`。それも拒否された場合は `stream_text()` が
  thinking 無しで1回だけ再試行する（出力開始前に限る）。
- **APIキーは ASCII でなければならない。** キーは `x-goog-api-key` ヘッダーに載るため、
  全角文字が残っていると httpx が `UnicodeEncodeError: 'ascii' codec can't encode...` を投げる
  （IME が全角モードのまま入力すると実際に起きる）。`config.normalize_api_key()` が NFKC 正規化で
  半角に直し、空白・改行・引用符も落とす。直しきれない場合は `get_client()` が
  `InvalidAPIKeyError` を投げる。例外は `APIKeyError` を基底に持ち、`ui.generate()` が
  まとめて `st.warning` に変換する。
- **描画をやめたウィジェットの値は Streamlit に破棄される。** 「入力済みなら入力欄を隠す」
  という出し分けをすると、隠した瞬間に値が消える。APIキー入力欄が実際にこれで壊れた
  （入力→「設定済み」表示→生成すると「キーが設定されていません」）。`app.py` の
  `api_key_section()` は、設定済みでも expander の中に入力欄を描画し続けることで回避している。
  また表示の分岐にはウィジェット自身の state（`api_key_input`）を見る。書き写し先の
  `api_key` は描画後にしか更新されず、判定が1実行分遅れるため。
- **`st.write_stream()` を使わないこと。** 入力を `is_dataframe_like()` で型判定する過程で
  pandas を読み込むため、Windows の Smart App Control が有効な環境では
  `pandas\_libs\parsers.cp312-win_amd64.pyd` がブロックされて生成が落ちる
  （CodeIntegrity イベントID 3033/3077）。代わりに `core/ui.py` の
  `stream_markdown()` を使う。同じ理由で `st.dataframe` / `st.table` /
  `st.line_chart` など pandas に依存するウィジェットも避けること。
- **ループ内で `result_actions()` を呼ぶときは `key=` を渡す。** 履歴一覧のように同じ
  ダウンロードボタンを複数描画すると DuplicateWidgetID になる。
- コンソールに日本語を出す検証コマンドは `PYTHONIOENCODING=utf-8` を付ける（cp932 で
  UnicodeEncodeError になる）。
