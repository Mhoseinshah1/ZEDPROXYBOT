#!/usr/bin/env bash
set -euo pipefail

read -rp "Bot Token: " BOT_TOKEN
read -rp "Admin ID عددی: " ADMIN_ID
read -rp "دامنه (اختیاری): " DOMAIN
read -rp "SSL فعال شود؟ (y/n): " SSL_ENABLED
read -rp "مسیر پنل مدیریت وب [/admin]: " ADMIN_PATH; ADMIN_PATH=${ADMIN_PATH:-/admin}
read -rp "مسیر API [/api]: " API_PATH; API_PATH=${API_PATH:-/api}
read -rp "Webhook Path [/bot/webhook]: " WEBHOOK_PATH; WEBHOOK_PATH=${WEBHOOK_PATH:-/bot/webhook}
read -rp "Chat ID گزارشات (اختیاری): " REPORT_CHAT
read -rp "شماره کارت: " CARD_NUMBER
read -rp "نام صاحب کارت: " CARD_HOLDER
read -rp "DB User [vpnbot]: " POSTGRES_USER; POSTGRES_USER=${POSTGRES_USER:-vpnbot}
read -rp "DB Pass [vpnbot]: " POSTGRES_PASSWORD; POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-vpnbot}
read -rp "DB Name [vpnbot]: " POSTGRES_DB; POSTGRES_DB=${POSTGRES_DB:-vpnbot}
read -rp "Redis URL [redis://redis:6379/0]: " REDIS_URL; REDIS_URL=${REDIS_URL:-redis://redis:6379/0}

SECRET_KEY=$(openssl rand -hex 32)
USE_WEBHOOK=false
WEBHOOK_URL=
if [[ -n "$DOMAIN" ]]; then
  USE_WEBHOOK=true
  WEBHOOK_URL="https://$DOMAIN$WEBHOOK_PATH"
fi

cat > .env <<ENV
SECRET_KEY=$SECRET_KEY
BOT_TOKEN=$BOT_TOKEN
ADMIN_TELEGRAM_ID=$ADMIN_ID
USE_WEBHOOK=$USE_WEBHOOK
WEBHOOK_URL=$WEBHOOK_URL
WEBHOOK_PATH=$WEBHOOK_PATH
DATABASE_URL=postgresql+asyncpg://$POSTGRES_USER:$POSTGRES_PASSWORD@db:5432/$POSTGRES_DB
REDIS_URL=$REDIS_URL
ADMIN_PATH=$ADMIN_PATH
API_PATH=$API_PATH
REPORT_CHAT_ID=$REPORT_CHAT
REPORT_ENABLED=false
POSTGRES_USER=$POSTGRES_USER
POSTGRES_PASSWORD=$POSTGRES_PASSWORD
POSTGRES_DB=$POSTGRES_DB
CARD_NUMBER=$CARD_NUMBER
CARD_HOLDER=$CARD_HOLDER
ENV

sudo apt update && sudo apt install -y docker.io docker-compose-plugin curl openssl
sudo systemctl enable --now docker

docker compose up -d --build

if [[ -n "$DOMAIN" && "$SSL_ENABLED" == "y" ]]; then
  sudo apt install -y certbot python3-certbot-nginx
  sudo certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos -m "admin@$DOMAIN" || true
fi

echo "نصب کامل شد."
