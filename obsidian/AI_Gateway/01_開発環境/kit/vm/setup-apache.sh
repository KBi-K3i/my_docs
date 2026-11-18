#!/usr/bin/env bash
# setup-apache.sh ── Lima VM（Rocky）の前段 httpd を一発構築する（冪等）
# 使い方:  sudo bash setup-apache.sh [ServerName] [上流URL]
#   例:    sudo bash setup-apache.sh aigw.local http://127.0.0.1:8000
# 内容:    httpd/mod_ssl 導入 → 自己署名証明書（無ければ作成）→ VirtualHost 配置
#          → configtest → 起動/自動起動 → firewalld 許可。SELinux は「拒否が出たら」方式（§後述の案内を表示）。
# 設計の正典: 02_Apacheリバースプロキシ設定.md（同梱ドキュメント）
set -euo pipefail

SERVER_NAME="${1:-aigw.local}"
UPSTREAM="${2:-http://127.0.0.1:8000}"
CONF=/etc/httpd/conf.d/ai-gateway.conf
CRT=/etc/pki/tls/certs/aigw.crt
KEY=/etc/pki/tls/private/aigw.key

if [ "$(id -u)" -ne 0 ]; then
  echo "ERROR: root で実行してください（sudo bash setup-apache.sh ...）" >&2
  exit 1
fi

echo "== [1/6] httpd / mod_ssl を導入"
dnf install -y httpd mod_ssl

echo "== [2/6] 自己署名証明書（既存なら再利用: $CRT）"
if [ ! -f "$CRT" ] || [ ! -f "$KEY" ]; then
  openssl req -x509 -newkey rsa:2048 -nodes -keyout "$KEY" -out "$CRT" -days 365 -subj "/CN=${SERVER_NAME}"
else
  echo "   既存の証明書を使う（作り直す場合は $CRT と $KEY を消して再実行）"
fi

echo "== [3/6] VirtualHost を配置: $CONF"
cat > "$CONF" <<EOF
<VirtualHost *:80>
    ServerName ${SERVER_NAME}

    ProxyPreserveHost On
    ProxyRequests Off
    ProxyPass        / ${UPSTREAM}/
    ProxyPassReverse / ${UPSTREAM}/

    RequestHeader set X-Forwarded-Proto "http"

    ProxyTimeout 300
    ErrorLog  /var/log/httpd/aigw_error.log
    CustomLog /var/log/httpd/aigw_access.log combined
</VirtualHost>

<VirtualHost *:443>
    ServerName ${SERVER_NAME}

    SSLEngine on
    SSLCertificateFile    ${CRT}
    SSLCertificateKeyFile ${KEY}

    ProxyPreserveHost On
    ProxyRequests Off
    ProxyPass        / ${UPSTREAM}/
    ProxyPassReverse / ${UPSTREAM}/

    RequestHeader set X-Forwarded-Proto "https"

    ProxyTimeout 300
    ErrorLog  /var/log/httpd/aigw_ssl_error.log
    CustomLog /var/log/httpd/aigw_ssl_access.log combined
</VirtualHost>
EOF

echo "== [4/6] 構文チェック"
apachectl configtest

echo "== [5/6] 起動・自動起動"
systemctl enable --now httpd
systemctl reload httpd

echo "== [6/6] firewalld（動いていれば http/https を恒久許可）"
if systemctl is-active --quiet firewalld; then
  firewall-cmd --permanent --add-service=http --add-service=https
  firewall-cmd --reload
else
  echo "   firewalld は停止中＝スキップ"
fi

echo
echo "完了。確認: curl -kI https://localhost/  （奥の gateway 未起動なら 502/503 が正常）"
echo "SELinux で転送が拒否される場合のみ（sudo ausearch -m avc -ts recent で denied を確認してから）:"
echo "  sudo setsebool -P httpd_can_network_connect on"
echo "Mac 側: Lima の portForwards に guestPort:80→hostPort:8080 / guestPort:443→hostPort:8443 を追加し、"
echo "        /etc/hosts に「127.0.0.1 ${SERVER_NAME}」を足して https://${SERVER_NAME}:8443 へ。"
