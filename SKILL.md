---
name: session-scribe
description: >
  Converts Claude Code session logs into structured knowledge articles (Markdown).
  Parses JSONL session logs from ~/.claude/projects/, extracts problem/approach/solution
  patterns, masks sensitive information (API keys, IPs, paths), and saves drafts to
  ~/knowledge-log/. Use when the user says "記事化", "ナレッジ化", "scribe", "記事にして",
  "セッションをまとめて", "knowledge", or wants to turn a session into an article.
when_to_use: >
  Trigger when the user wants to convert AI session history into a reusable document.
  Common phrases: "記事化して", "ナレッジ化", "まとめて", "記事にして", "scribe",
  "ログを記事に", "セッションを保存", "knowledge article", "write up this session".
argument-hint: "[project-name or session-id]"
allowed-tools:
  - Bash
  - Read
  - Write
  - Glob
  - Grep
  - Edit
---

# session-scribe

AIセッションの対話ログを、構造化されたナレッジ記事（Markdown）に変換するSkill。

## 処理フロー

### ステップ1: セッションログの特定

まずセッション一覧を取得する:

```!
python3 "${CLAUDE_SKILL_DIR}/scripts/parse_session.py"
```

- `$ARGUMENTS` にプロジェクト名やセッションIDが指定されている場合はそれで絞り込む
- `$ARGUMENTS` が空の場合は、**現在のセッション以外で最新のもの**を提案する
- 複数候補がある場合はユーザーに選択を求める

### ステップ2: ログのパースとマスキング

対象セッションが決まったら、パースとマスキングをパイプラインで実行する:

```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/parse_session.py" "<セッションJSONLのパス>" | python3 "${CLAUDE_SKILL_DIR}/scripts/mask_secrets.py"
```

出力されたトランスクリプトを読み、記事の構造化に進む。

### ステップ3: 記事の構造化

パース・マスキング済みの会話ログから、以下の構造でMarkdown記事を作成する。

#### トラブルシュート系セッションの場合

```markdown
# [タイトル: 具体的で検索しやすいもの]

## 環境

- OS / 言語 / ライブラリバージョン（セッションから抽出）

## 発生した問題

[何が起きたか、エラーメッセージ等]

## 試したこと

1. [アプローチ1] → 結果・失敗理由
2. [アプローチ2] → 結果・失敗理由
3. [アプローチ3] → 成功

## 解決方法

[最終的な解決策とコード]

## 学び

[なぜこの解決策が効いたか、次回への教訓]
```

#### それ以外のセッション（設計相談、コードレビュー等）

テンプレートに固執せず、セッション内容に適した構造にする。
例: 「設計判断」「実装のポイント」「検討した代替案」等のセクション。

#### 構造化のルール

- **タイトル**: 具体的で検索しやすいもの（例: 「Proxmox VEでZFS poolのimportに失敗する問題の解決」）
- **環境**: セッション中のコマンド出力やエラーメッセージからOS、言語、バージョンを抽出
- **発生した問題**: ユーザーの最初の質問やエラーメッセージから要約
- **試したこと**: 時系列で試行錯誤を列挙。失敗したアプローチも含める
- **解決方法**: 最終的に成功した方法をコード付きで記述
- **学び**: なぜその解決策が効いたか、根本原因の理解
- **複数の話題を含むセッション**: 話題ごとに別の記事に分割する

### ステップ4: 保存

Writeツールで `~/knowledge-log/` ディレクトリに直接保存する。

- ファイル名: `YYYY-MM-DD_タイトル.md`
- 記事末尾にメタデータコメントを付与:

```markdown
---

<!-- session-scribe metadata
session_id: <元のセッションID>
project: <プロジェクト名>
generated: <生成日時>
tool: session-scribe
-->
```

### ステップ5: 結果報告

保存完了後、ユーザーに以下を報告する:

- 生成した記事の数
- 各記事のタイトルとファイルパス
- マスキングした秘匿情報の種類と件数（あれば）
- 「修正が必要な箇所があれば教えてください」

## 注意事項

- セッションログには秘匿情報が含まれる可能性がある。**必ずマスキングを行う**
- ユーザーの許可なく記事を外部に公開・送信しない
- 現在のセッション自体を記事化する場合は、このSkillの処理内容は含めない
- 出力は日本語で行う（ユーザーが英語で依頼した場合は英語）
