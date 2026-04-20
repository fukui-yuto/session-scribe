# session-scribe 開発計画

## 開発条件

- 開発時間: 週10h(平日夜 + 週末)
- 並行タスク: AWS SAP資格学習、ポートフォリオRAGプロジェクト
- 開発期間: **4週間**(Skill化により短縮)

## プロダクト形態

**Claude Skill 単体** としてMVPを作る。

### なぜSkillか(確定事項)

- LLM API料金不要(ユーザーのClaude契約で動作)
- 開発コスト最小(SKILL.md + 補助スクリプト)
- Claudeエコシステムに乗れる(2026年4月時点で急速拡大中、anthropics/skillsは87,000+ stars)
- 配布が楽(GitHub + 将来的にMarketplace)
- オープン標準化されており将来Claudeに縛られない
- skill-creatorで初期ドラフトをClaude自身に作らせられる

## 技術スタック

| 領域 | 技術 |
|---|---|
| Skill本体 | SKILL.md(Markdown + YAML frontmatter) |
| スクリプト | Python(ログパース、マスキング、ファイル保存) |
| LLM処理 | Claude本体に任せる(Skill経由で) |
| ストレージ | ローカルMarkdownファイル |
| 配布 | GitHubリポジトリ + 将来Plugin Marketplace |

**不要になった要素**: FastAPI、SQLite、HTMX、Webダッシュボード、LLM API連携コード、pip配布。

## プロジェクト構成(確定)

```
session-scribe/
├── .git/
├── .gitignore
├── README.md
├── SKILL.md              ← Skillの本体(Claudeが読む指示書)
├── scripts/
│   ├── parse_session.py  ← Claude Codeログをパース
│   ├── mask_secrets.py   ← 秘匿情報マスキング
│   └── save_draft.py     ← Markdown保存
├── templates/
│   └── draft_template.md ← 生成記事のテンプレート
├── examples/
│   └── sample_output.md  ← 期待される出力例
└── docs/
    └── setup.md          ← インストール手順
```

## 4週間タスク分解

### Week 1: 基盤調査・設計

#### Day 1: ローカル環境セットアップ

```bash
cd ~/dev    # お好みの場所
mkdir session-scribe
cd session-scribe
git init
mkdir -p scripts templates examples docs
touch README.md SKILL.md .gitignore
touch scripts/.gitkeep templates/.gitkeep examples/.gitkeep docs/.gitkeep
```

`.gitignore`の中身:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
.venv/
env/
ENV/
*.egg-info/
.pytest_cache/

# IDE
.vscode/
.idea/
*.swp
*.swo
.DS_Store

# Secrets / 個人設定
.env
.env.local
config.local.*

# テスト用データ(個人セッションログが紛れ込むのを防ぐ)
test_data/
sample_sessions/
*.jsonl

# 生成物
output/
drafts/
```

重要: `*.jsonl`を除外することで、開発中に手元のセッションログ(秘匿情報含む)をGitに上げない。

#### Day 2: Claude Codeログの構造調査

```bash
ls -la ~/.claude/projects/
ls ~/.claude/projects/ | head -5
find ~/.claude/projects/ -name "*.jsonl" -type f | head -3
head -5 ~/.claude/projects/<プロジェクト名>/<セッションID>.jsonl | python3 -m json.tool --json-lines
```

調査してメモすべきこと:

1. `~/.claude/projects/`配下のディレクトリ構造
2. JSONLの1行(1レコード)のフィールド(`role`, `content`, `timestamp`等)
3. 1セッションあたりの行数(数十〜数百?)
4. 記事化に使えそうな気になるフィールド

#### Day 3: 既存Skillの雰囲気を掴む

- https://github.com/anthropics/skills を眺める
- 既存Skillを2〜3個読んで構造・書き方を掴む
- 特に似た用途(ファイル読み書き系)のSkillに注目

#### Day 4-5: SKILL.mdの雛形

- skill-creatorを使って初期ドラフトを生成
- Claude Codeと相談しながらSKILL.mdを書く
- YAML frontmatterの`name`と`description`を慎重に設計(トリガー精度に直結)

#### Day 6-7: 最小スクリプト

- `parse_session.py`: JSONLを読んで辞書のリストに変換する最小機能
- 動作確認: 自分のセッションログ1つをパースできること

### Week 2: LLM構造化(最重要週)

- SKILL.mdに構造化手順を詳細に書き込む
- 「課題/試行/解決」を抽出するための指示を練る
- 自分の過去セッション5〜10件でドッグフーディング
- 出力品質が安定するまでプロンプト調整

**成果**: 1セッション → 1Markdownが安定して動く

### Week 3: マスキング + 仕上げ

- `mask_secrets.py`: 正規表現ベース
  - APIキー(sk-, AIza等のパターン)
  - IPアドレス(プライベートIP範囲)
  - メールアドレス
  - パス(/home/ユーザー名、/Users/ユーザー名)
- エッジケース対応
- `save_draft.py`完成
- 自分で日常使用(ドッグフーディング開始)

### Week 4: ローンチ準備

- README整備(セットアップ手順、使い方、スクリーンショット)
- `docs/setup.md`執筆
- GitHub公開
- 紹介記事(Zenn)執筆: 「Claude Codeのログを記事化するSkillを作った話」
- デモGIF作成
- X(Twitter)、Discord等で告知

## 成功指標(ローンチ時)

- GitHub公開完了
- README・setup.md整備完了
- 自分で1週間以上ドッグフーディングしている
- 紹介記事公開

## 成功指標(ローンチ後3ヶ月)

- GitHub Star: 200+
- 実ユーザー(ダウンロード後1週間継続使用): 50+
- 自身のドッグフーディング: 週2セッション以上を3ヶ月継続
- Anthropic公式Marketplace掲載(努力目標)

## 時間配分の推奨

- **SAP学習**: 朝・昼(平日の通勤、昼休み等)
- **開発**: 夜・週末
- 脳の使う部位が違うので切り替えが効く

## 次のアクション(今日やること)

1. `~/dev/session-scribe/`をローカルに作成
2. Day 1のgit initとディレクトリ作成
3. `.gitignore`を配置
4. Day 2のClaude Codeログ調査に着手

**Day 1-2の結果をClaude Codeに共有すれば、Week 2の具体実装に進める。**

## 重要な設計思想(忘れないため)

- **作らない判断が最重要**: MVPは「削りきる」こと
- **Skill形態のまま無理に機能追加しない**: 重い機能は将来のWebアプリで
- **ユーザーのローカルで完結**: データを外部に送らないのが最大の訴求点
- **公開フローは手動でいい**: 最初の10記事は手動コピペで十分
- **LLM構造化の品質がプロダクトの価値**: SKILL.mdの設計に最も時間を使う
