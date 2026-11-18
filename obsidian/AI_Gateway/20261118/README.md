# ai_gateway ── litellm×2＋Redis 構成（動作確認済み・2026-11-18）

ブラウザ → web(Flask:5000) ／ gateway(FastAPI:8000) → litellm-lb(nginx:4000) → litellm-1 / litellm-2 → LLMプロバイダ（既定: Vertex AI）。
litellm は db(Postgres=台帳) と redis(状態共有・spendバッファ) を使う。全6サービス＋認証補助ワンショット1つ。

## 設計方針（プロバイダ入れ替え可能）

秘密・資格情報への依存は「`.env` の環境変数」と「`secrets/` に置くファイル」の2つだけにしてある。
特定のクラウドCLIやコンテナにスタック本体は依存しない。

- Vertex AI を使う: 認証JSON（サービスアカウント鍵でも ADC でも可）を `secrets/` に置き、`.env` の `GOOGLE_APPLICATION_CREDENTIALS` でそのパスを指す
- OpenAI 等に替える: `.env` のキーを差し替え、`litellm_config.yaml` の `model_list` を書き替える（compose・コードは無改修）
- compose 内の `gcloud` サービスは「鍵JSONを用意できない場合に ADC を作る任意の補助」で、削除しても本体は動く

## ファイル構成

| ファイル | 役割 |
|---|---|
| `.devcontainer/compose.yaml` | 本体（litellm×2＋LB＋Redis＋db＋gateway/web。認証補助 `gcloud` は profiles で通常起動から除外） |
| `.devcontainer/compose.dev.yaml` | 開発上書き（gateway/web を sleep 待機にする） |
| `.devcontainer/Dockerfile` | gateway/web 用イメージ（Python3.12＋uv） |
| `.devcontainer/devcontainer.json` | VS Code の Reopen in Container 用 |
| `litellm_config.yaml` | LiteLLM 設定（Redis有効版・この1枚のみ） |
| `litellm_lb.conf` | nginx の振り分け定義（litellm-1/-2） |
| `.env` / `.env.example` | 全キーに初期値入り（設定もれ防止。実値が要るのはプロバイダ節だけ） |
| `secrets/` | 認証ファイルの置き場（コミットしない。litellm が読み取り専用で参照） |
| `src/ai_api_gateway/main.py` | gateway 仮実装（LiteLLM へ中継・学習で書き換える前提） |
| `web/app.py` | web 仮実装（最小のリクエスト画面・AIボタン＝gateway を fetch） |

## 起動

```bash
cd .devcontainer && docker compose up -d --build
```

`docker compose ps` で db・redis・litellm-1・litellm-2 が `healthy`、gateway・web・litellm-lb が `Up` になること。

## LLMプロバイダ認証（Vertex AI の場合・初回のみ）

認証JSONを `secrets/` に置く。入手方法は2通りで、どちらのJSONでも置き方・使い方は同じ。

**方式A（推奨・鍵ファイルを配布される場合）**: サービスアカウント鍵 JSON を `secrets/` に置き、`.env` の `GOOGLE_APPLICATION_CREDENTIALS=/secrets/<ファイル名>` を合わせる。

**方式B（鍵が無い場合・ADCを作る）**: 補助ワンショットを使う（gcloud はこのコンテナ内だけ＝ホスト導入不要）。

```bash
docker compose run --rm gcloud
```

表示された URL をブラウザで開いてログインし、コードを貼り戻す。`secrets/application_default_credentials.json` ができる。

どちらの方式でも、置いたあとに litellm へ反映する:

```bash
docker compose restart litellm-1 litellm-2
```

## 疎通確認

```bash
curl http://localhost:4000/health/liveliness
```

```bash
curl -H "Authorization: Bearer sk-dummy-master-key-0000" http://localhost:4000/v1/models
```

```bash
curl http://localhost:8000/healthz
```

ブラウザで `http://localhost:5000` を開き「AIに送る」→ gateway → LB → litellm → プロバイダの1往復。
（認証ファイル設置前はプロバイダ段で「/secrets/... not found」が返る＝鎖はそこまで通っている、の確認になる）

## .env の方針

全キーにラボでそのまま動く初期値を入れてある（設定もれで起動失敗しないため）。
`LITELLM_SALT_KEY` は一度 DB に保存が始まったら変えない（変えると復号不能）。
外部公開する場合はダミーキーを強い値に差し替える。
