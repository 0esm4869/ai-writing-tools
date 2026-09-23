# ✍️ AI ライティングスタジオ

Python + Streamlit + Gemini API で作った、個人用のAIライティングツール集です。
データベースも認証もなし。ローカルで起動して、そのまま使えます。

## 収録ツール

| ツール | できること |
| --- | --- |
| ✍️ ブログ記事作成 | テーマから構成案 → 本文まで。文字数・読者・トーン指定つき |
| 📧 メール作成・返信 | 受信メールを貼るだけで返信案。件名から署名まで完成形で出力 |
| 📝 要約 | 箇条書き / 3行 / 議事録スタイルなど6形式 × 4段階の分量 |
| 🔍 校正・推敲 | 誤字脱字・表記ゆれ・敬語を修正し、指摘一覧も表示 |
| 🔁 リライト・トーン変換 | 内容を保ったまま文体と分量だけ変更 |
| 🌐 翻訳 | 12言語。用語集の指定と訳注つき |
| 📣 SNS投稿文 | X / Instagram / LinkedIn など媒体別に複数案 |
| 💡 アイデア出し | タイトル案・キャッチコピー・記事ネタを角度を変えて量産 |
| 💬 フリーチャット | 型のない相談や、生成結果の手直し用 |
| 🕘 履歴 | 生成結果をローカル保存。検索・再ダウンロード・削除 |

出力はすべてストリーミング表示。生成結果は `.md` / `.txt` でダウンロードできます。

## セットアップ

```bash
# 1. 依存パッケージ
python -m venv .venv
.venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt

# 2. APIキー
copy .env.example .env          # macOS/Linux: cp .env.example .env
# .env を開いて GEMINI_API_KEY に自分のキーを貼り付ける
```

APIキーは [Google AI Studio](https://aistudio.google.com/apikey) で無料で取得できます。
`.env` を作らず、アプリのサイドバーから直接入力することもできます（その場合はセッション中だけ有効）。

## 起動

`run_app.bat` をダブルクリックするだけです。ブラウザで `http://localhost:8501` が自動で開きます。
終了するときは、開いた黒いウィンドウで `Ctrl + C` を押してください。

コマンドから起動する場合:

```bash
.venv\Scripts\activate
streamlit run app.py
```

## サイドバーの設定

- **モデル** — APIキーを設定すると、使えるモデルが自動で一覧表示されます。一覧に出ないモデルを
  使いたい場合は「生成の詳細設定」の「モデルIDを直接指定」に入力してください
- **創造性 (temperature)** — 低いほど堅実、高いほど多様な表現に
- **熟考モード** — 生成前に思考を挟んで精度を上げる（その分遅い）

## ディレクトリ構成

```
run_app.bat            ダブルクリック起動用（依存パッケージも自動でセットアップ）
app.py                 エントリポイント。サイドバーとページ振り分け
core/
  config.py            APIキーの取得、モデル一覧、生成パラメータ
  gemini.py            Gemini API のラッパー（ストリーミング／チャット）
  prompts.py           全ツールのプロンプト。出力の質を変えたいときはここ
  history.py           履歴の保存（data/history.json）
  ui.py                共通UI部品（入力欄・生成・保存ボタン）
tools/                 各ツールの画面。1ツール1ファイル
data/history.json      生成履歴（自動生成・gitignore 済み）
.streamlit/config.toml Streamlit の設定（メール入力プロンプトと利用統計を無効化）
```

## カスタマイズのヒント

- **出力の質を変えたい** → `core/prompts.py` のシステムプロンプトを編集
- **選択肢を増やしたい** → 各 `tools/*.py` 冒頭の定数リスト（`TONES`, `STYLES` など）に追記
- **ツールを追加したい** → `tools/` に `render()` を持つファイルを作り、`app.py` の `PAGES` に登録
