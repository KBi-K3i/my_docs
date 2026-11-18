# 閲覧キット ── ドキュメント（md）を読む人向けの最小セット

*個人側の実リポジトリから書き出した配布用コピー（2026-11-18 同期・正は個人 Vault）*

コード・設計書を**読むだけ**（編集してもMarkdown程度）の人向け。DevContainer は使わず、**clone して VS Code で開くだけ**で整うようにする。

## 仕組み ── 配るのは settings.json ではなく extensions.json

拡張機能を勧める公式の仕組みは **`.vscode/extensions.json`（ワークスペース推奨拡張）**。リポジトリに同梱しておくと、フォルダを開いた人に「このワークスペースには推奨拡張があります」と通知が出て、**ワンクリックで一括インストール**できる（拡張ビューで `@recommended` と検索しても一覧が出る）。settings.json は「設定」を配る器であって拡張は入らない——**2つの合わせ技**が正解。

推奨リストは閲覧の最小4つ：

| 拡張ID | なぜ閲覧に要るか |
|---|---|
| `bierner.markdown-mermaid` | **構成図（Mermaid）をプレビューで描画**する。標準プレビューはMermaid非対応＝これが無いと図がコードのまま |
| `MS-CEINTL.vscode-language-pack-ja` | UI の日本語化 |
| `DavidAnson.vscode-markdownlint` | Markdown を少し編集する人向けの記法チェック |
| `mhutchie.git-graph` | ブランチ・履歴をグラフで眺める（読む人の「いつ変わった？」に効く） |

## 本命の形 ── 独立「閲覧キット」リポジトリ＋対象リポジトリの develop を subtree で内蔵

閲覧専用の小さなリポジトリを1つ作り、そこに **対象リポジトリの develop ブランチを `git subtree` で取り込む**。subtree は相手の内容を**このリポジトリの中身としてコピーで抱える**ので、閲覧者は**素の `git clone` 1回で全部入り**——追加の操作もフラグも要らない（ここが submodule との決定的な違い）。

```
viewer-kit/                     ← 閲覧キットリポジトリ（職場の Git ホスティングに作る）
├─ .vscode/
│  ├─ extensions.json           ← このフォルダの同名ファイルをコピー
│  └─ settings.json             ← 同上（Markdown折り返し）
├─ README.md                    ← 閲覧者向けの一言（下の2行だけ書けば足りる）
└─ repo/                        ← 対象リポジトリの develop が丸ごと入る（subtree）
```

**管理者（あなた）の作業**——キットリポジトリの直下で、初回に1回：

```bash
git subtree add --prefix=repo <対象リポジトリURL> develop --squash
```

対象の develop が進んだら取り直す（随時）：

```bash
git subtree pull --prefix=repo <対象リポジトリURL> develop --squash
```

`--squash` は相手の履歴を1コミットに畳んで取り込む指定＝キット側の履歴が汚れない（`git subtree -h`／`man git-subtree` で実機確認済み・git 2.43）。

**閲覧者の作業**——これだけ：

```bash
git clone <閲覧キットのURL>
```

開く → 右下の「推奨拡張機能をインストールしますか？」で Install → `Ctrl+Shift+V` でプレビュー（Mermaid も描画される）。

> [!NOTE]
> **submodule との使い分け**：`git submodule add -b develop <URL> repo` でも「別リポジトリの develop を参照」はできるが、閲覧者側に `git clone --recurse-submodules`（または clone 後の `git submodule update --init`）という**忘れがちな一手**が要り、忘れると `repo/` が空に見える。更新を閲覧者自身が `git submodule update --remote` で取れる利点はあるものの、「ほぼ何もせずすぐ使える」が狙いなら **subtree が適役**。鮮度の責任は管理者の `subtree pull` に集まる＝更新時にひと声かける運用とセットで。

> [!NOTE]
> **簡易版（リポジトリを増やしたくない場合）**：対象リポジトリ自体の `.vscode/` に extensions.json を同梱する形でも、直 clone する閲覧者には同じ体験になる（実体リポジトリには同梱済み）。独立キットが効くのは「複数リポジトリを束ねて見せたい」「開発リポジトリの clone 権限を配りたくない」とき。

## 任意：うっかり編集防止（optional-user-settings.jsonc）

「読むだけのつもりがコードを触ってしまう」のを防ぎたい人向けに、**Markdown 以外を読み取り専用**にする個人設定を同梱した（`files.readonlyInclude`／`files.readonlyExclude`＝VS Code 1.79 で追加された公式設定）。リポジトリには入れない＝**開発者まで読み取り専用になってしまうため**。使う人が自分のユーザー settings.json に貼る。
