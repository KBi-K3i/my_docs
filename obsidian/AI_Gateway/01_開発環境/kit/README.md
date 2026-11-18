# 環境構築キット ── 1台版（お試し）／2台版（開発の本命）／4台版（運用サンプル）

*個人側の実リポジトリから書き出した配布用コピー（2026-11-18 同期・正は個人 Vault）*

[開発環境構築ドキュメント](../00_環境構築手順.md) §4〜§5 の設計を、そのまま使えるファイルにしたキット。規模×Redis の組み合わせは次のとおり（2026-11-18 方針）。

| 版 | Redisなし | Redisあり | 開発モード（sleep待機） |
|---|---|---|---|
| **1台版**（お試し・最低限の成果） | `devcontainer/compose.single.yaml`（これのみ＝Redis不要） | — | — |
| **2台版**（**開発の本命**） | `devcontainer/compose.x2-noredis.yaml`（比較・段階導入用） | `devcontainer/compose.yaml`＝既定 | `compose.yaml`＋`compose.dev.yaml` |
| **4台版**（将来サイジングの運用サンプル） | `deploy/compose.noredis.yaml` | `deploy/compose.yaml` | — |

起動コマンド（`.devcontainer/` で実行。4台版のみ `deploy/` で）：

```bash
docker-compose up -d --build
```

```bash
docker-compose -f compose.single.yaml up -d --build
```

```bash
docker-compose -f compose.x2-noredis.yaml up -d --build
```

```bash
cd deploy && docker-compose up -d --build
```

```bash
docker-compose -f compose.yaml -f compose.dev.yaml up -d --build
```

## config は2枚＝ファイルで切替（編集不要）

| ファイル | 中身 | 使う compose |
|---|---|---|
| `repo-root/litellm_config.yaml` | **Redisなし・既定** | 1台版・各 noredis 版 |
| `repo-root/litellm_config.redis.yaml` | **Redis 3点セット有効** | 2台版あり・4台版あり |

> [!NOTE]
> **noredis 版の注意**：公式の線引きは「ワーカープロセスが2つ以上なら Redis」。2台/4台の noredis 版では、レート制限・予算カウンタがインスタンスごとに別勘定（実効値が台数倍）になる。挙動比較・段階導入の学習用であり、複数台の常用は Redisあり版にする。

## 配置方法

| このフォルダ | リポジトリでの置き場所 |
|---|---|
| `devcontainer/` の中身 | `.devcontainer/` へ（フォルダ名の先頭に `.` を付ける） |
| `repo-root/` の中身 | リポジトリ直下へ（config 2枚・`litellm_lb.conf`＝2台用・`.env.example`） |
| `deploy/` | リポジトリ直下へフォルダごと（4台版 compose 2枚＋4台用 `litellm_lb.conf`） |
| `vm/` の中身 | リポジトリ外＝**VM ホストで実行するスクリプト**（`sudo bash` で実行・[Apache設定](../02_Apacheリバースプロキシ設定.md)） |

パッケージ名は `ai_gateway`（`src/ai_gateway/`）を仮置きしている。実プロジェクトの名前に合わせて compose の `command:` を読み替える。

## 注意

- **gateway/web の `command:` 自走は、`main:app`（FastAPI）と `web/app.py`（Flask）の実装後に生きる**。実装前は開発モード（sleep 待機）で上げて作業する。
- GW からの LiteLLM 接続先は、複数版＝**`http://litellm-lb:4000`**・1台版＝**`http://litellm:4000`**。★実装では接続先を `.env` で外出しにすると、規模の切替がアプリ無改修になる。
- Redisあり版は `.env` に `REDIS_HOST=redis`・`REDIS_PORT=6379` を入れる。
- **台数を変える**ときは、compose の `litellm-N` サービス（YAMLアンカー `*litellm` の行）と `litellm_lb.conf` の `server` 行を同数にするだけ。
- `.env` は `.env.example` を複製して各自が作る（コミットしない）。`.gitignore` の `.env.*` パターンには `!.env.example` の除外行を足す。
- **前段の httpd（リバースプロキシ／TLS終端）はコンテナ外＝VM ホストの仕事**。`vm/setup-apache.sh` で一発構築できる。GCP との疎通は [GCP疎通確認（1台版）](../03_GCP疎通確認（1台版）.md)。
