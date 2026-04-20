# session-scribe

AIとの対話を、自動で検索可能な個人ナレッジに変える Claude Skill。

## 何ができるか

Claude Codeでのトラブルシュートや開発セッションの内容を、構造化されたMarkdown記事に自動変換します。

```
ユーザー: 「今日のセッション、ナレッジ化しておいて」
   ↓
session-scribe:
  1. セッションログ（JSONL）をパース
  2. 秘匿情報を自動マスキング
  3. 「課題 → 試行 → 解決」形式で構造化
  4. ~/knowledge-log/ にMarkdown保存
   ↓
「3件のセッションを記事化しました」
```

## 特徴

- **ゼロ設定**: Claude Codeのセッションログをそのまま読み取り
- **自動マスキング**: APIキー、IPアドレス、ユーザーパス等を自動検出・置換
- **ローカル完結**: データは外部に送信されません
- **LLM API不要**: ユーザーのClaude契約内で動作

## インストール

```bash
# Claude Code Skillとしてインストール
claude skill install github:yuto/session-scribe
```

または手動でクローン:

```bash
git clone https://github.com/yuto/session-scribe.git
```

詳細は [docs/setup.md](docs/setup.md) を参照。

## 使い方

Claude Codeのセッション中に:

```
/session-scribe
```

または自然言語で:

```
今日のセッションを記事化して
このセッションをナレッジにまとめて
```

## 出力例

```markdown
# Proxmox VEでZFS poolのimportに失敗する問題の解決

## 環境
- OS: Proxmox VE 8.3
- ストレージ: ZFS on Linux

## 発生した問題
クラスタ再起動後、ZFS poolが自動マウントされない...

## 試したこと
1. `zpool import` → プールが見つからない
2. `zpool import -f` → 成功

## 解決方法
...

## 学び
...
```

完全な出力例は [examples/sample_output.md](examples/sample_output.md) を参照。

## プロジェクト構成

```
session-scribe/
├── SKILL.md              ← Skill本体
├── scripts/
│   ├── parse_session.py  ← セッションログパーサー
│   ├── mask_secrets.py   ← 秘匿情報マスキング
│   └── save_draft.py     ← 記事保存
├── templates/
│   └── draft_template.md ← 記事テンプレート
├── examples/
│   └── sample_output.md  ← 出力例
└── docs/
    └── setup.md          ← セットアップ手順
```

## 動作要件

- Claude Code v2.0以上
- Python 3.10以上（標準ライブラリのみ使用）

## ライセンス

MIT
