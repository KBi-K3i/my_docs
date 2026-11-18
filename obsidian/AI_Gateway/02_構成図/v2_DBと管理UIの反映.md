# 構成図 v2 ── DBと管理UIの反映

*個人検討ノートの一般化版（2026-11-18 同期・正は個人 Vault）*

> [!NOTE]
> **この版は何か**
> 2026-11-18 朝に筆者が手打ちで作成した版。v1 までの「論点の注記」中心から一歩進め、**LiteLLM まわりの実体（PostgreSQL コンテナ・テーブル群・管理者用 Web UI・ポート）を描き込んだ**。同日に AI アシスタントが litellm-docs（ローカルクローン＋公式サイト）で機械照合し、タイポと事実関係を修正。さらに同日のレビュー合意で、判定群の位置・v1注記・外向き通信の描き方を調整した（修正内容は下の変更点・詳細は [論点台帳](../03_論点台帳.md) §5）。未決の論点を先取りしている箇所には図中に ※ を残している。

## 変更点（v1 → v2）

- **PostgreSQL 用コンテナを新設**。LiteLLM のデータベース実体として 5432 番ポートと、公式スキーマどおりのテーブル群（`LiteLLM_OrganizationTable`・`LiteLLM_TeamTable`・`LiteLLM_UserTable`・`LiteLLM_EndUserTable`、および論点に直結する `LiteLLM_VerificationToken`〔仮想キー〕・`LiteLLM_SpendLogs`〔支出ログ〕）を描いた。GW の組織検証・利用者検証は、v1 の自前「記録データベース（バインドマウント）」ではなく、このDBを PostgreSQL プロトコルで参照する形に改めた（※ただし台帳 §3「記録DBの選定」「spend反映のタイミング」は保留のまま＝直読みか管理API経由かは未決。図は選択肢の一つを描いた仮置き）。
- **LiteLLM Proxy コンテナの実体を描き込み**。4000 番ポートの API・管理者用 Web UI（`http://localhost:4000/ui`）・`DATABASE_URL` 環境変数を追加した。
- **利用者を2役に分割**。「システム利用者」と「ゲートウェイ管理者」を分け、管理者→ LiteLLM Admin UI の経路を足した。
- **機械照合による修正（2026-11-18 AI アシスタント）**：`litell_db`→`litellm_db`・`api`→`api_key`（タイポで宙に浮いていたノードを接続）／`PostgresSQL`→`PostgreSQL`／DBアクセスの注記「60分毎？」→ 公式確認の内容（spend 系はバッチ書き込み・本番推奨は60秒毎、既定の間隔は調査中）へ差し替え／テーブル名に `LiteLLM_` 接頭辞を付与／末尾の余分なコードフェンスを削除。
- **レビュー合意による調整（2026-11-18 同日・筆者回答）**：①状態判定・ログ出力・データ形式変換・例外処理を v1 どおり「利用管理アプリケーション」の中へ戻した。②v1の注記を復元（httpd＝リバースプロキシ／TLS終端・`api_key`＝LiteLLMの鍵で `.env` 渡し〔台帳 §4 決定済み〕・WEBアプリケーション＝ログイン・本人確認はここ）。③GCPへの外向き通信は、コンテナ内の「443番ポート」をやめ（443は宛先＝GCP側のポートで、コンテナ側が待ち受けるのではないため）、**ホストの「外向き通信の出口（NAT）」を経由する線**として描いた（2026-11-18 筆者指摘＝ホストを通る口を図に残す、を反映。「宛先443」の表記は筆者指定で省略）。ただし公式確認のとおり**コンテナの外向き接続は既定で可能**で、`ports:`（公開設定）は「外からコンテナへ」の方向専用＝**外向きのために compose.yaml に書く項目は無い**[^docker-egress]。送信元ポートも固定でなく、OSが接続ごとに自動で割り当てる（エフェメラルポート）。この旨は図の注記にも明記した。④GW→LiteLLM の線の受け手を `proxy_api`（v1のノード名の名残＝v2では未定義で宙に浮いていた。機械照合でも見落とし）から `port4000` へ筆者が付け替え＝コンテナの公開ポートに合流する正しい形。⑤**compose.yaml に書く/書かないの見える化**（2026-11-18 筆者指摘＝「書く必要が無いならそれが分かるように」）：コンテナ間通信の「Podman NW IF」の箱を新設し、`ports:` に書く公開ポート（80番・4000番＋Admin UI 用ポート）を**オレンジ実線**、書かない口（Podman NW・外向きNAT・5432番）を**青点線**で塗り分け、図の下に凡例を付けた。⑥**Redis 用コンテナを追加**（2026-11-18 同日・説明用）：compose の5サービス化（開発環境構築 §5.1.4）に合わせ、6379番ポートと Redis（インスタンス間の状態共有・spendバッファ）の箱を描いた。litellm からの線は**点線＝箱のみで未接続**（有効化は性能規模の与件＝ピーク見積りの確認後）を表し、6379番は `ports:` に書かない口なので青点線スタイル。

```mermaid
flowchart TD

	subgraph users["利用者"]
	
		system_user["システム利用者"]
		gw_admin["ゲートウェイ管理者"]
	
	end
	
	system_user =="https"==> app
	gw_admin == "LiteLLM Web UI" ==> ui_port ==> port4000
	
	subgraph system["業務システム"]
	
		app["WEB アプリケーション<br>（ログイン＝本人確認はここ）"]
		apigw_if["AI API ゲートウェイ インターフェース"]
	
		app <=="共通フォーマット<br>(JSON等 ※未定)"==> apigw_if
	end
	
	apigw_if =="https"==> httpd
	httpd =="https"==> apigw_if
	psql_protocol_1 <--"Podman NW"--> port5432
	psql_protocol_2 <--"Podman NW"--> port5432
	
	subgraph host_server["ホストサーバー"]
	
		httpd["httpd/apache<br>（リバースプロキシ／TLS終端）"]
		log_dir["ログ出力用ディレクトリ"]
		ui_port["LiteLLM Admin UI 用ポート"]
		
		httpd =="HTTP REQ ※内部http/https未定"==> port80
		port80 =="HTTP RES"==> httpd
		
		port80 --> gw_if
		gw_if --> port80
		
		subgraph virtual_key_db["PostgreSQL 用コンテナ"]
		
			port5432["5432番ポート"]
			litellm_db["LiteLLM データベース"]
			port5432 --- litellm_db
			litellm_db --- org_tbl["LiteLLM_OrganizationTable"]
			litellm_db --- team_tbl["LiteLLM_TeamTable"]
			litellm_db --- user_tbl["LiteLLM_UserTable"]
			litellm_db --- euser_tbl["LiteLLM_EndUserTable"]
			litellm_db --- vkey_tbl["LiteLLM_VerificationToken<br>（仮想キー）"]
			litellm_db --- spend_tbl["LiteLLM_SpendLogs<br>（支出ログ※バッチ書き込み）"]
		
		end
		
		subgraph redis_container["Redis 用コンテナ"]
		
			port6379["6379番ポート"]
			redis_store["Redis<br>（インスタンス間の状態共有・spendバッファ）<br>※箱のみ＝有効化は性能規模の与件確認後"]
			port6379 --- redis_store
		
		end
		
		subgraph gw_container["GW用コンテナ"]
		
			port80[80番ポート]
			api_key["API キー＝LiteLLMの鍵<br>（.env＝環境変数で渡す）"]
			
			api_key -."認証ヘッダで渡す".-> proxy_if
			
			subgraph gw_app["利用管理アプリケーション"]
			
				gw_if["GWインターフェース<br>（FastAPI）"]
				proxy_if["プロキシ用インターフェース"]
				psql_protocol_1["PostgreSQL プロトコル"]
			
				subgraph judgment["状態判定"]

					check_organization["組織検証（使用制限の判定）"]
					check_user["利用者検証（使用制限の判定）<br>※本人確認は業務システム側／ここはトークン検証"]
					check_req_body["入力値の検証（画像、PDFの形式含む）"]
					continuous{"通過可能判定<br>（検証を全て通過したか）※定義は要確認"}
					availability["利用可能な判定<br>（残枠・権限があるか）※定義は要確認"]

				end

				exp(("例外処理")) =="エラー応答"==> gw_if
				exp -.-> logging
				availability -.-> logging

				logging["ログ出力<br>（本文は残さない＝機密）"]
				convertor["データ形式変換"]

				continuous --"NO"--> exp
				continuous --"YES"--> availability

				gw_if =="共通フォーマット"==> judgment
				
				check_organization -."DB参照".-> psql_protocol_1
				check_user -."DB参照".-> psql_protocol_1

				check_organization --> continuous
				check_user --> continuous
				check_req_body --> continuous

				availability =="共通フォーマット"==> convertor

				proxy_if ==> convertor
				convertor ==> proxy_if
				convertor =="共通フォーマット"==> gw_if
			
			end
		
		end
		
		podman_nw["Podman NW IF<br>（コンテナ間通信＝サービス名で解決）<br>※compose.yaml の ports: 記載は不要"]
		
		proxy_if <=="end-user識別子を付与"==> podman_nw
		podman_nw <==> port4000
		
		subgraph llm_proxy["LiteLLM Proxy 用コンテナ"]
		
			port4000["4000番ポート"]
			psql_protocol_2["PostgreSQL プロトコル"]
			admin_ui["管理者用 Web UI"]
			litellm_api["LiteLLM API"]
			env["環境変数<br>DATABASE_URL"]
			
			env -.-> litellm_api
			
			litellm_api <-- "DBアクセス<br>※spend系はバッチ書き込み＝間隔は要調査（本番推奨60秒毎）" --> psql_protocol_2
			
			litellm_api <--> port4000
			litellm_api --"http://localhost:4000/ui"--- admin_ui
			
		end
		
		litellm_api -."※有効化時（状態共有・spendバッファ）".-> port6379
		
		logging -."ローテーション".-> log_dir
		
		egress_nat["外向き通信の出口（NAT）<br>送信元ポート＝OSが自動割当（エフェメラル）<br>※compose.yaml への記載は不要（ports: は内向き公開専用）"]
		
		litellm_api <=="https"==> egress_nat
	
	end

	egress_nat <=="https"==> service_account

subgraph GCP

	service_account["サービスアカウント<br>（Vertex用・GCP発行／共通1つが既定）"]
	vertex["Vertex AI"]

	service_account --> vertex
	vertex --> service_account

end

classDef compose_port fill:#ffe9c9,stroke:#d68400,stroke-width:2px
classDef no_compose fill:#e8f4ff,stroke:#2b6cb0,stroke-dasharray: 4 3
class port80,port4000,ui_port compose_port
class podman_nw,egress_nat,port5432,port6379 no_compose

```

> [!NOTE]
> **凡例 ── compose.yaml に書くポート・書かない口**
> **オレンジ実線＝`ports:`（公開）に書く口**。80番ポート（ホストの httpd がGWコンテナへ入るため）と、4000番ポート＋ホスト側の Admin UI 用ポート（管理者が外から UI へ入るため）。公開＝「外からコンテナへ」の方向を開ける設定である。
> **青点線＝compose.yaml の `ports:` に書かない口**。コンテナ間（GW⇔LiteLLM・GW/LiteLLM⇔Postgres の 5432番・LiteLLM⇔Redis の 6379番〔有効化時〕）は Podman NW 上でサービス名により解決され、公開は不要。GCP への外向きは NAT 経由で既定のまま可能＝送信元ポートは OS が接続ごとに自動割当（エフェメラル）なので、そもそも固定の番号を書けない[^docker-egress]。

## 出典（一次情報）

2026-11-18 取得・逐語は `curl`＋`grep` で機械照合済み。

- [Networking overview（Docker 公式）](https://docs.docker.com/engine/network/) ── 外向き接続は既定で可能・`-p`/`--publish`（`ports:`）は外からの公開用

## 脚注

[^docker-egress]: 原文「Containers have networking enabled by default, and they can make outgoing connections.」（コンテナは既定でネットワークが有効になっており、外向きの接続を行える）、および「Use the `--publish` or `-p` flag to make a port available outside the host」（`--publish`／`-p` フラグは、ポートをホストの外から利用可能にするために使う）＝公開設定は「外から中へ」の方向のための仕組み。— [Networking overview（Docker 公式）](https://docs.docker.com/engine/network/)
