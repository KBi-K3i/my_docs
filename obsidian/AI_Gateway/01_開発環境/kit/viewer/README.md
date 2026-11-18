# 閲覧キット ── ドキュメント（md）を読む人向けの最小セット

*個人側の実リポジトリから書き出した配布用コピー（2026-11-18 同期・正は個人 Vault）*

コード・設計書を**読むだけ**（編集してもMarkdown程度）の人向け。DevContainer は使わず、**clone して VS Code で開くだけ**で整うようにする。

## 仕組み ── 配るのは settings.json ではなく extensions.json

拡張機能を勧める公式の仕組みは **`.vscode/extensions.json`（ワークスペース推奨拡張）**。リポジトリに同梱しておくと、フォルダを開いた人に「このワークスペースには推奨拡張があります」と通知が出て、**ワンクリックで一括インストール**できる（拡張ビューで `@recommended` と検索しても一覧が出る）。settings.json は「設定」を配る器であって拡張は入らない——**2つの合わせ技**が正解。

| ファイル | 役割 | 配布方法 |
|---|---|---|
| `extensions.json` | 閲覧用の推奨拡張（下の4つ） | リポジトリの `.vscode/` に**コミットして同梱**（閲覧者は何もしない） |
| リポジトリの `settings.json` | Markdown の折り返し等（開発設定と同居・閲覧者に無害） | 同上 |
| `optional-user-settings.jsonc` | うっかり編集防止（任意・個人設定） | 使いたい閲覧者だけが**自分のユーザー settings.json に貼る** |

開発者の拡張は `.devcontainer/devcontainer.json` 側で（コンテナ内に）自動導入されるので、この推奨リストは**閲覧の最小4つ**に絞ってある：

| 拡張ID | なぜ閲覧に要るか |
|---|---|
| `bierner.markdown-mermaid` | **構成図（Mermaid）をプレビューで描画**する。標準プレビューはMermaid非対応＝これが無いと図がコードのまま |
| `MS-CEINTL.vscode-language-pack-ja` | UI の日本語化 |
| `DavidAnson.vscode-markdownlint` | Markdown を少し編集する人向けの記法チェック |
| `mhutchie.git-graph` | ブランチ・履歴をグラフで眺める（読む人の「いつ変わった？」に効く） |

## 閲覧者の手順（実質2ステップ）

develop ブランチだけを取得して開く：

```bash
git clone -b develop --single-branch <リポジトリURL>
```

```bash
code <クローンしたフォルダ>
```

右下に出る「**推奨拡張機能をインストールしますか？**」で Install を押す（通知を逃したら拡張ビューで `@recommended`）。以上——Markdown は `Ctrl+Shift+V`（プレビュー）で、Mermaid の構成図も描画される。

## 任意：うっかり編集防止（optional-user-settings.jsonc）

「読むだけのつもりがコードを触ってしまう」のを防ぎたい人向けに、**Markdown 以外を読み取り専用**にする個人設定を同梱した（`files.readonlyInclude`／`files.readonlyExclude`＝VS Code 1.79 で追加された公式設定）。リポジトリには入れない＝**開発者まで読み取り専用になってしまうため**。使う人が自分のユーザー settings.json に貼る。
