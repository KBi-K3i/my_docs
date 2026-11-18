# 環境構築キット ── compose 3枚＋DevContainer 資材一式（一般化版）

*個人側の実リポジトリから書き出した配布用コピー（2026-11-18 同期・正は個人側＝直接編集しない）*

[開発環境構築ドキュメント](../00_環境構築手順.md) §4〜§5 の設計を、そのまま使えるファイルにしたキット。構成は3モードで、**どの compose を読むかだけで切り替わる**（中身の書き換え不要）。

## 配置方法

| このフォルダ | リポジトリでの置き場所 |
|---|---|
| `devcontainer/` の中身 | `.devcontainer/` へ（フォルダ名の先頭に `.` を付ける） |
| `repo-root/` の中身 | リポジトリ直下へ |
| `vm/` の中身 | リポジトリ外＝**VM ホストで実行するスクリプト**（配置不要・VM へ持ち込んで `sudo bash` で実行） |

パッケージ名は `ai_gateway`（`src/ai_gateway/`）を仮置きしている。実プロジェクトの名前に合わせて compose の `command:`（`ai_gateway.main:app`）を読み替える。

## 3モードの起動

**① 単体・Redisあり（本体のみ＝5サービスが自走）**

```bash
cd .devcontainer && docker-compose up -d --build
```

**② 単体・Redisなし（4サービス）**

```bash
cd .devcontainer && docker-compose -f compose.noredis.yaml up -d --build
```

**③ DevContainer運用（Redisあり＋sleep待機・VS Code の Reopen in Container と同じ2枚）**

```bash
cd .devcontainer && docker-compose -f compose.yaml -f compose.dev.yaml up -d --build
```

素の `docker-compose up -d` が①になるのは、Compose が既定で `compose.yaml`（と、あれば `compose.override.yaml`）しか読まないため（詳細と出典＝[開発環境構築ドキュメント](../00_環境構築手順.md) §5.1）。

## 注意

- **gateway/web の `command:` 自走は、`main:app`（FastAPI）と `web/app.py`（Flask）の実装後に生きる**。実装前は③（sleep待機）で上げ、`exec` で入って作業する。
- `.env` は `.env.example` を複製して各自が作る（コミットしない）。`.gitignore` に `.env` を入れる場合、`.env.*` のようなパターンは `.env.example` まで無視するので `!.env.example` の除外行を足す。
- Redis の機能有効化は `repo-root/litellm_config.yaml` のコメントを外し、`.env` の `REDIS_*` を設定する（手順＝同ドキュメント §5.1.4）。撤去は逆に消すだけ。
- **前段の httpd（リバースプロキシ／TLS終端）はコンテナ外＝VM ホストの仕事**。`vm/setup-apache.sh` で一発構築できる（手順と設計＝[Apache リバースプロキシ設定](../02_Apacheリバースプロキシ設定.md)）。
