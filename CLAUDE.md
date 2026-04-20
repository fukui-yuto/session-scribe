# session-scribe

AIセッションログを自動で構造化されたナレッジ記事に変換するClaude Skill。

## プロジェクト概要

- **形態**: Claude Skill（SKILL.md + 補助Pythonスクリプト）
- **目的**: Claude Codeのセッションログを「課題/試行/解決」形式の記事に変換
- **出力先**: `~/knowledge-log/` にMarkdownとして保存
- **対象ログ**: `~/.claude/projects/` 配下のJSONLファイル

## ディレクトリ構成

```
session-scribe/
├── SKILL.md              ← Skill本体（Claudeが読む指示書）
├── scripts/
│   ├── parse_session.py  ← セッションログのパース
│   ├── mask_secrets.py   ← 秘匿情報のマスキング
│   └── save_draft.py     ← Markdown保存
├── templates/
│   └── draft_template.md ← 記事テンプレート
├── examples/
│   └── sample_output.md  ← 出力例
└── docs/
    └── setup.md          ← セットアップ手順
```

## 技術スタック

- Skill本体: SKILL.md（Markdown + YAML frontmatter）
- スクリプト: Python 3.10+（標準ライブラリのみ）
- LLM処理: Claude本体（Skill経由）
- ストレージ: ローカルMarkdown

## 開発ルール

- 外部ライブラリは使わない（標準ライブラリのみ）
- コメント・ドキュメントは日本語で記述
- `*.jsonl` はgitに含めない（秘匿情報保護）
- ユーザーのデータは外部に送信しない（ローカル完結）

## セッションログの形式

`~/.claude/projects/<エンコードされたパス>/<セッションID>.jsonl`

各行はJSONオブジェクトで、主要なtypeは:
- `user`: ユーザーメッセージ（content は文字列 or 配列）
- `assistant`: アシスタント応答（text, tool_use, thinking を含む）
- `progress`: ツール実行の進捗
- `file-history-snapshot`: ファイル変更のスナップショット
- `system`: システムメッセージ

## よく使うコマンド

```bash
# セッション一覧を表示
python scripts/parse_session.py

# 特定セッションをパース
python scripts/parse_session.py <jsonl_path>

# テキストのマスキングテスト
echo "test" | python scripts/mask_secrets.py
```
