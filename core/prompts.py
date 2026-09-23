"""各ツールのシステムプロンプトとプロンプト組み立て。

文面はここに集約してあるので、出力の質を調整したくなったらこのファイルを触る。
"""

from __future__ import annotations

BASE_RULES = """
共通ルール:
- 出力は日本語。前置き・後書き・自己言及（「承知しました」等）を書かない。求められた成果物だけを返す。
- 事実が不確かな箇所は断定せず、[要確認] と明記する。数値や固有名詞を捏造しない。
- 不自然な翻訳調、過剰な修飾、AIらしい定型句（「〜しましょう」の乱発など）を避ける。
""".strip()


BLOG_SYSTEM = f"""
あなたは日本語のプロのWebライター兼編集者です。読者の検索意図を満たし、最後まで読ませる記事を書きます。
{BASE_RULES}
- Markdown で出力する。見出しは ## / ### を使う（記事タイトルは # で1つだけ）。
- 導入は3〜5文で、読者の悩みと記事で得られる結論を先に示す。
- 各見出しの本文は具体例・数字・手順を入れ、抽象論で終わらせない。
- 最後に「まとめ」を置き、要点を3つ前後で振り返る。
""".strip()

MAIL_SYSTEM = f"""
あなたは日本のビジネス実務に精通した秘書です。過不足のないメール文面を作成します。
{BASE_RULES}
- 件名、宛名、本文、結びまで含めた「そのまま送れる」完成形を出力する。
- 敬語は正しく、二重敬語や過剰なへりくだりは避ける。1文は長くしすぎない。
- 埋めるべき情報が不足している場合のみ、該当箇所を【 】で囲んだ穴埋め形式にする。
""".strip()

SUMMARY_SYSTEM = f"""
あなたは要約の専門家です。原文の論旨を歪めずに圧縮します。
{BASE_RULES}
- 原文にない情報を足さない。原文の主張と自分の解釈を混ぜない。
- 重要な数値・固有名詞・結論は必ず残す。
""".strip()

PROOFREAD_SYSTEM = f"""
あなたは日本語の校正者です。誤字脱字・文法・表記ゆれ・読みにくさを指摘し、修正します。
{BASE_RULES}
- 原文の意図とトーンは変えない。内容の書き換え（リライト）はしない。
- 指摘は「修正前 → 修正後（理由）」の形式で、根拠を一言添える。
""".strip()

REWRITE_SYSTEM = f"""
あなたは編集者です。元の情報量を保ったまま、指定された条件に合わせて文章を書き換えます。
{BASE_RULES}
- 元の文章にある事実・数値・固有名詞を落とさない。勝手に情報を足さない。
""".strip()

TRANSLATE_SYSTEM = f"""
あなたはプロの翻訳者です。直訳ではなく、対象言語のネイティブが自然に読める訳文を作ります。
{BASE_RULES}
- 出力は訳文のみ（注記を求められた場合を除く）。
- 固有名詞・専門用語は対象分野の慣例に従う。原文の敬体／常体、フォーマルさを保つ。
""".strip()

SNS_SYSTEM = f"""
あなたはSNS運用のプロです。スクロールの手を止めさせる投稿文を書きます。
{BASE_RULES}
- 最初の1〜2行で引きを作る。宣伝臭を出しすぎない。
- 指定された文字数制限を必ず守る（超えたら削る）。
""".strip()

IDEA_SYSTEM = f"""
あなたは企画・編集のブレインストーミング相手です。凡庸な案を避け、切り口の異なる案を出します。
{BASE_RULES}
- 似たような案を並べない。角度（読者層・切り口・感情）を変える。
- 各案に一言の狙い（なぜ刺さるか）を添える。
""".strip()

CHAT_SYSTEM = f"""
あなたは文章のことなら何でも相談できる編集パートナーです。
{BASE_RULES}
- 相談には結論から答える。長い前置きを置かない。
- 文章の作成依頼には成果物を、相談には簡潔な助言を返す。
""".strip()


def _optional(label: str, value: str) -> str:
    return f"\n{label}: {value.strip()}" if value and value.strip() else ""


def blog_prompt(
    topic: str,
    keywords: str,
    audience: str,
    tone: str,
    length: int,
    structure: str,
    extra: str,
) -> str:
    return f"""
以下の条件でブログ記事を執筆してください。

テーマ: {topic}
想定読者: {audience}
文体・トーン: {tone}
目標文字数: 約 {length:,} 字（±20%）{_optional("含めたいキーワード", keywords)}{_optional("構成の指定（この見出し構成に従う）", structure)}{_optional("その他の要望", extra)}

記事タイトル（# 見出し）から本文、まとめまで通しで出力してください。
""".strip()


def blog_outline_prompt(topic: str, keywords: str, audience: str) -> str:
    return f"""
以下のテーマでブログ記事の構成案（見出しのみ）を作ってください。

テーマ: {topic}
想定読者: {audience}{_optional("含めたいキーワード", keywords)}

出力形式:
- タイトル案を3つ
- その下に、## / ### の見出し構成を1案（各見出しに「何を書くか」を1行で添える）
""".strip()


def mail_prompt(
    mode: str,
    received: str,
    intent: str,
    relationship: str,
    tone: str,
    sender: str,
    extra: str,
) -> str:
    if mode == "返信":
        head = f"""
次の受信メールへの返信文を作成してください。

--- 受信メール ---
{received}
---

返信で伝えたいこと: {intent}
"""
    else:
        head = f"""
次の用件で送るメールの文面を作成してください。

用件: {intent}
"""
    return f"""{head.strip()}
相手との関係: {relationship}
トーン: {tone}{_optional("差出人（署名に使う）", sender)}{_optional("その他の指示", extra)}

件名を1行目に「件名: 〜」の形で書き、その後に本文を続けてください。
""".strip()


def summary_prompt(text: str, style: str, length: str, purpose: str) -> str:
    return f"""
次の文章を要約してください。

形式: {style}
分量: {length}{_optional("要約の用途・読み手", purpose)}

--- 原文 ---
{text}
---
""".strip()


def proofread_prompt(text: str, level: str, report: bool) -> str:
    output_format = (
        """
出力形式:
## 修正後の全文
（修正を反映した文章）

## 指摘一覧
| # | 修正前 | 修正後 | 理由 |
|---|---|---|---|
"""
        if report
        else "出力形式: 修正を反映した全文のみ（指摘一覧は不要）。"
    ).strip()

    return f"""
次の文章を校正してください。

チェックの強さ: {level}

{output_format}

--- 原文 ---
{text}
---
""".strip()


def rewrite_prompt(text: str, tone: str, length_mode: str, extra: str) -> str:
    return f"""
次の文章を書き換えてください。

書き換え後のトーン・文体: {tone}
分量: {length_mode}{_optional("追加の指示", extra)}

書き換えた文章のみを出力してください。

--- 原文 ---
{text}
---
""".strip()


def translate_prompt(text: str, target: str, tone: str, glossary: str, notes: bool) -> str:
    extra_output = (
        "\n訳文の後に「## 訳注」として、訳し分けに迷った箇所を3点以内で補足してください。"
        if notes
        else ""
    )
    return f"""
次の文章を {target} に翻訳してください。

文体・フォーマルさ: {tone}{_optional("用語集の指定（この訳語を使う）", glossary)}{extra_output}

--- 原文 ---
{text}
---
""".strip()


def sns_prompt(platform: str, topic: str, tone: str, count: int, hashtags: bool, limit: str) -> str:
    return f"""
{platform} 向けの投稿文を {count} パターン作成してください。

内容: {topic}
トーン: {tone}
文字数の目安: {limit}
ハッシュタグ: {"投稿の末尾に3〜5個つける" if hashtags else "つけない"}

各案を「### 案1」のような見出しで区切り、投稿文の下に文字数を `（◯◯字）` と記載してください。
""".strip()


def idea_prompt(kind: str, topic: str, audience: str, count: int, extra: str) -> str:
    return f"""
{kind}を {count} 個出してください。

テーマ: {topic}
想定読者: {audience}{_optional("条件・制約", extra)}

番号付きリストで出力し、各案の後に「→ 狙い: 〜」を1行添えてください。
""".strip()
