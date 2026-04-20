# session-scribe セットアップ手順

## 前提条件

- Claude Code がインストール済み（v2.0以上）
- Python 3.10 以上
- Claude Codeのセッションログが `~/.claude/projects/` に存在すること

## インストール

### 方法1: Skill として直接インストール

```bash
claude skill install github:yuto/session-scribe
```

### 方法2: 手動インストール

1. リポジトリをクローン:

```bash
git clone https://github.com/yuto/session-scribe.git
```

2. Claude Codeのskillsディレクトリにシンボリックリンクを作成:

```bash
# Linuxの場合
ln -s /path/to/session-scribe ~/.claude/skills/session-scribe

# Windowsの場合（管理者権限のコマンドプロンプト）
mklink /D "%USERPROFILE%\.claude\skills\session-scribe" "C:\path\to\session-scribe"
```

## 使い方

### 基本

Claude Codeのセッション中に以下のように入力:

```
/session-scribe
```

または自然言語で:

```
今日のセッションを記事化して
```

### 特定のセッションを指定

```
/session-scribe proxmox-lab
```

### 出力先

記事は `~/knowledge-log/` に Markdown ファイルとして保存されます。

```
~/knowledge-log/
├── 2026-04-20_Proxmox-VEでCorosync通信の問題を解決.md
├── 2026-04-19_Terraformのstate-lockエラー対処.md
└── ...
```

## 設定

### 出力先の変更

デフォルトの出力先は `~/knowledge-log/` です。変更する場合は環境変数を設定:

```bash
export SESSION_SCRIBE_OUTPUT_DIR="$HOME/my-knowledge"
```

## トラブルシューティング

### セッションログが見つからない

Claude Codeのログが `~/.claude/projects/` に存在するか確認:

```bash
ls ~/.claude/projects/
```

### Python 3が見つからない

```bash
python3 --version
```

Python 3.10以上が必要です。

### マスキングが効きすぎる/足りない

`scripts/mask_secrets.py` のパターンを必要に応じて調整してください。
