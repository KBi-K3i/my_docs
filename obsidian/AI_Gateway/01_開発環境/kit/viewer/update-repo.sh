#!/usr/bin/env bash
# update-repo.sh ── 閲覧キットに対象リポジトリの develop を取り込む／更新する（管理者用・冪等）
# subtree には .gitmodules のような宣言ファイルが無いため、取り込み定義をこのスクリプトでファイル化している。
# 使い方: 閲覧キットリポジトリの直下で
#   bash update-repo.sh                         （下の既定値で add または pull）
#   bash update-repo.sh <リポジトリURL> [ブランチ] [取り込み先]
# 取り込んだ結果は通常のファイルとしてコミットされる＝閲覧者は素の git clone だけで全部入り。
set -euo pipefail

REPO_URL="${1:-git@example.com:group/ai-gateway.git}"   # ★対象リポジトリのURLに書き換える
BRANCH="${2:-develop}"
PREFIX="${3:-repo}"

if [ ! -d .git ]; then
  echo "ERROR: 閲覧キットリポジトリの直下（.git がある場所）で実行してください" >&2
  exit 1
fi

if [ -d "$PREFIX" ]; then
  echo "== 既存の $PREFIX/ を $BRANCH の最新へ更新（git subtree pull）"
  git subtree pull --prefix="$PREFIX" "$REPO_URL" "$BRANCH" --squash
else
  echo "== 初回取り込み（git subtree add）: $REPO_URL の $BRANCH → $PREFIX/"
  git subtree add --prefix="$PREFIX" "$REPO_URL" "$BRANCH" --squash
fi

echo
echo "完了。push すれば、閲覧者は git clone だけで $PREFIX/ 込みの全部入りを取得できる。"
