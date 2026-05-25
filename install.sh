#!/usr/bin/env bash
set -euo pipefail
sudo apt-get update -y
sudo apt-get install -y docker.io docker-compose-plugin curl
sudo systemctl enable --now docker

read -rp 'Bot Token: ' BOT_TOKEN
read -rp 'Admin ID عددی: ' MAIN_ADMIN_ID
read -rp 'دامنه (اختیاری): ' DOMAIN
read -rp 'SSL فعال شود؟ (y/n): ' SSL_ANSWER
read -rp 'مسیر پنل وب [/admin]: ' ADMIN_PATH; ADMIN_PATH=${ADMIN_PATH:-/admin}
read -rp 'مسیر API [/api]: ' API_PATH; API_PATH=${API_PATH:-/api}
read -rp 'مسیر webhook [/bot/webhook]: ' BOT_WEBHOOK_PATH; BOT_WEBHOOK_PATH=${BOT_WEBHOOK_PATH:-/bot/webhook}
read -rp 'Chat ID گزارشات (اختیاری): ' REPORT_GROUP_CHAT_ID
read -rp 'شماره کارت: ' CARD_NUMBER
read -rp 'نام صاحب کارت: ' CARD_HOLDER
read -rp 'DB Name [zedproxy]: ' DB_NAME; DB_NAME=${DB_NAME:-zedproxy}
read -rp 'DB User [zedproxy]: ' DB_USER; DB_USER=${DB_USER:-zedproxy}
read -rsp 'DB Pass [zedproxy]: ' DB_PASS; DB_PASS=${DB_PASS:-zedproxy}; echo
read -rp 'Redis URL [redis://redis:6379/0]: ' REDIS_URL; REDIS_URL=${REDIS_URL:-redis://redis:6379/0}

SSL_ENABLED=false; [[ "$SSL_ANSWER" =~ ^[Yy]$ ]] && SSL_ENABLED=true
cp .env.example .env
sed -i "s|^BOT_TOKEN=.*|BOT_TOKEN=${BOT_TOKEN}|" .env
sed -i "s|^MAIN_ADMIN_ID=.*|MAIN_ADMIN_ID=${MAIN_ADMIN_ID}|" .env
sed -i "s|^DOMAIN=.*|DOMAIN=${DOMAIN}|" .env
sed -i "s|^SSL_ENABLED=.*|SSL_ENABLED=${SSL_ENABLED}|" .env
sed -i "s|^ADMIN_PATH=.*|ADMIN_PATH=${ADMIN_PATH}|" .env
sed -i "s|^API_PATH=.*|API_PATH=${API_PATH}|" .env
sed -i "s|^BOT_WEBHOOK_PATH=.*|BOT_WEBHOOK_PATH=${BOT_WEBHOOK_PATH}|" .env
sed -i "s|^REPORT_GROUP_CHAT_ID=.*|REPORT_GROUP_CHAT_ID=${REPORT_GROUP_CHAT_ID}|" .env
sed -i "s|^REPORT_GROUP_ENABLED=.*|REPORT_GROUP_ENABLED=$([[ -n \"$REPORT_GROUP_CHAT_ID\" ]] && echo true || echo false)|" .env
sed -i "s|^CARD_NUMBER=.*|CARD_NUMBER=${CARD_NUMBER}|" .env
sed -i "s|^CARD_HOLDER=.*|CARD_HOLDER=${CARD_HOLDER}|" .env
sed -i "s|^DATABASE_URL=.*|DATABASE_URL=postgresql+psycopg://${DB_USER}:${DB_PASS}@db:5432/${DB_NAME}|" .env
sed -i "s|^REDIS_URL=.*|REDIS_URL=${REDIS_URL}|" .env

if [[ -n "$DOMAIN" ]]; then
  echo "server_name ${DOMAIN};" >/tmp/server_name.txt
fi

docker compose up -d --build

if [[ -n "$DOMAIN" && "$SSL_ENABLED" == "true" ]]; then
  sudo apt-get install -y certbot python3-certbot-nginx
  sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "admin@${DOMAIN}" || true
fi

echo '✅ نصب انجام شد.'
