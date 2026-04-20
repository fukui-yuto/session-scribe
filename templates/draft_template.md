# {{title}}

## 環境

- OS: {{os}}
- 言語/ランタイム: {{language}}
- 関連ツール/ライブラリ: {{tools}}

## 発生した問題

{{problem_description}}

## 試したこと

{{#each attempts}}
### {{@index}}. {{approach}}

{{description}}

{{#if failed}}
**結果**: 失敗 — {{failure_reason}}
{{else}}
**結果**: 成功
{{/if}}

{{/each}}

## 解決方法

{{solution}}

```{{language}}
{{solution_code}}
```

## 学び

{{learnings}}

---

*この記事は [session-scribe](https://github.com/yuto/session-scribe) で生成されました。*
