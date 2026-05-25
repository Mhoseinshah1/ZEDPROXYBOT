#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Mhoseinshah1/ZEDPROXYBOT.git"
INSTALL_DIR="/opt/zedproxybot"
BACKUP_DIR="$INSTALL_DIR/backups"

msg(){ echo -e "\e[1;36m$1\e[0m"; }
err(){ echo -e "\e[1;31m$1\e[0m"; }
warn(){ echo -e "\e[1;33m$1\e[0m"; }

compose_cmd(){
  if docker compose version >/dev/null 2>&1; then echo "docker compose"; return; fi
  if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; return; fi
  return 1
}

ensure_deps(){
  msg "بررسی پیش‌نیازها..."
  command -v git >/dev/null 2>&1 || { sudo apt-get update -y && sudo apt-get install -y git; }
  if ! command -v docker >/dev/null 2>&1; then
    msg "Docker نصب نیست. در حال نصب..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER" || true
  fi
  if ! compose_cmd >/dev/null 2>&1; then
    warn "Docker Compose یافت نشد. در حال نصب plugin..."
    sudo apt-get update -y && sudo apt-get install -y docker-compose-plugin || true
  fi
  compose_cmd >/dev/null 2>&1 || { err "Docker Compose نصب نشد."; exit 1; }
}

random_secret(){ openssl rand -hex 32; }

prompt_env(){
  read -rp "Bot Token: " BOT_TOKEN
  read -rp "Main Admin ID (عددی): " MAIN_ADMIN_ID
  read -rp "Admin username [main_admin]: " ADMIN_USERNAME; ADMIN_USERNAME=${ADMIN_USERNAME:-main_admin}
  read -rsp "Admin password: " ADMIN_PASSWORD; echo
  read -rp "دامنه (اختیاری): " DOMAIN
  read -rp "فعال‌سازی SSL؟ (yes/no) [no]: " SSL_ENABLE; SSL_ENABLE=${SSL_ENABLE:-no}
  read -rp "Chat ID گروه گزارشات (اختیاری): " REPORT_GROUP_CHAT_ID
  read -rp "نام دیتابیس [zedproxy]: " DB_NAME; DB_NAME=${DB_NAME:-zedproxy}
  read -rp "یوزر دیتابیس [zedproxy]: " DB_USER; DB_USER=${DB_USER:-zedproxy}
  read -rsp "پسورد دیتابیس (خالی=random): " DB_PASSWORD; echo
  DB_PASSWORD=${DB_PASSWORD:-$(openssl rand -hex 12)}
  read -rp "Redis URL [redis://redis:6379/0]: " REDIS_URL; REDIS_URL=${REDIS_URL:-redis://redis:6379/0}

  JWT_SECRET=$(random_secret)
  USE_WEBHOOK=false; [[ -n "$DOMAIN" ]] && USE_WEBHOOK=true
  REPORT_GROUP_ENABLED=false; [[ -n "$REPORT_GROUP_CHAT_ID" ]] && REPORT_GROUP_ENABLED=true
  WEB_BASE_URL=""; [[ -n "$DOMAIN" ]] && WEB_BASE_URL="https://$DOMAIN"

  cat > "$INSTALL_DIR/.env" <<EOF
APP_NAME=ZedProxyBot
ENV=production
BOT_TOKEN=$BOT_TOKEN
MAIN_ADMIN_ID=$MAIN_ADMIN_ID
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_PASSWORD=$ADMIN_PASSWORD
JWT_SECRET=$JWT_SECRET
JWT_EXPIRE_MINUTES=120
DATABASE_URL=postgresql+psycopg://$DB_USER:$DB_PASSWORD@db:5432/$DB_NAME
REDIS_URL=$REDIS_URL
DOMAIN=$DOMAIN
WEB_BASE_URL=$WEB_BASE_URL
USE_WEBHOOK=$USE_WEBHOOK
BOT_WEBHOOK_PATH=/bot/webhook
ADMIN_PATH=/admin
API_PATH=/api
CARD_NUMBER=
CARD_HOLDER=
K2K_ENABLED=false
REPORT_GROUP_CHAT_ID=$REPORT_GROUP_CHAT_ID
REPORT_GROUP_ENABLED=$REPORT_GROUP_ENABLED
FORCE_JOIN_ENABLED=false
FORCE_PHONE_ENABLED=false
EOF
  msg ".env ساخته شد: $INSTALL_DIR/.env"
}

run_migrate_seed(){
  local C; C="$(compose_cmd)"
  (cd "$INSTALL_DIR" && $C up -d --build)
  (cd "$INSTALL_DIR" && $C exec -T app sh -c 'alembic upgrade head || true')
  (cd "$INSTALL_DIR" && $C exec -T app python -m app.db.init_db)
}

health_check(){
  sleep 3
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then msg "Health check موفق بود."; else warn "Health check ناموفق بود."; fi
}

backup_db(){
  mkdir -p "$BACKUP_DIR"
  local C; C="$(compose_cmd)"
  local ts file
  ts=$(date +"%Y%m%d_%H%M%S")
  file="$BACKUP_DIR/db_backup_$ts.sql"
  (cd "$INSTALL_DIR" && $C exec -T db pg_dump -U zedproxy zedproxy > "$file")
  msg "بکاپ انجام شد: $file"
}

restore_db(){
  mkdir -p "$BACKUP_DIR"
  mapfile -t files < <(ls -1 "$BACKUP_DIR"/*.sql 2>/dev/null || true)
  [[ ${#files[@]} -eq 0 ]] && { warn "بکاپی یافت نشد."; return; }
  echo "بکاپ‌ها:"; for i in "${!files[@]}"; do echo "$((i+1)). ${files[$i]}"; done
  read -rp "شماره بکاپ: " idx
  file="${files[$((idx-1))]:-}"
  [[ -z "$file" ]] && { err "انتخاب نامعتبر."; return; }
  read -rp "آیا مطمئن هستید؟ (yes/no): " c; [[ "$c" != "yes" ]] && return
  local C; C="$(compose_cmd)"
  (cd "$INSTALL_DIR" && cat "$file" | $C exec -T db psql -U zedproxy -d zedproxy)
  msg "ری‌استور انجام شد."
}

install_robot(){
  ensure_deps
  if [[ ! -d "$INSTALL_DIR/.git" ]]; then
    sudo mkdir -p /opt
    sudo chown -R "$USER":"$USER" /opt
    git clone "$REPO_URL" "$INSTALL_DIR"
  else
    msg "پروژه قبلاً نصب شده است."
  fi
  [[ -f "$INSTALL_DIR/.env" ]] || prompt_env
  run_migrate_seed
  local C; C="$(compose_cmd)"
  (cd "$INSTALL_DIR" && $C ps)
  health_check
}

update_robot(){
  [[ -d "$INSTALL_DIR/.git" ]] || { err "پروژه نصب نشده است."; return; }
  ensure_deps
  backup_db
  cd "$INSTALL_DIR"
  git checkout main || true
  git fetch origin || { err "git fetch شکست خورد"; return; }
  git pull origin main || { err "git pull شکست خورد"; return; }
  local C; C="$(compose_cmd)"
  $C build
  $C up -d
  $C exec -T app sh -c 'alembic upgrade head || true'
  $C restart app bot
  $C ps
  health_check
  msg "آپدیت انجام شد."
}

remove_robot(){
  [[ -d "$INSTALL_DIR" ]] || { warn "نصب موجود نیست."; return; }
  read -rp "آیا مطمئن هستید که می‌خواهید حذف کنید؟ (yes/no): " c; [[ "$c" != "yes" ]] && return
  warn "پیشنهاد: قبل از حذف از گزینه بکاپ استفاده کنید."
  local C; C="$(compose_cmd)"
  cd "$INSTALL_DIR"
  $C down || true
  read -rp "volumeها هم حذف شوند؟ (yes/no): " v
  [[ "$v" == "yes" ]] && $C down -v || true
  read -rp "مسیر پروژه حذف شود؟ (yes/no): " d
  [[ "$d" == "yes" ]] && rm -rf "$INSTALL_DIR"
  msg "حذف انجام شد."
}

restart_services(){ local C; C="$(compose_cmd)"; cd "$INSTALL_DIR"; $C restart app bot; $C ps; }
status_services(){ local C; C="$(compose_cmd)"; cd "$INSTALL_DIR"; $C ps; }
logs_bot(){ local C; C="$(compose_cmd)"; cd "$INSTALL_DIR"; $C logs -f bot; }
logs_app(){ local C; C="$(compose_cmd)"; cd "$INSTALL_DIR"; $C logs -f app; }

while true; do
  echo
  msg "ZedProxyBot Manager"
  echo "1) Install bot"
  echo "2) Update bot"
  echo "3) Remove bot"
  echo "4) Backup database"
  echo "5) Restore database"
  echo "6) Restart services"
  echo "7) Service status"
  echo "8) View bot logs"
  echo "9) View app logs"
  echo "10) Exit"
  read -rp "Select option: " choice
  case "$choice" in
    1) install_robot ;;
    2) update_robot ;;
    3) remove_robot ;;
    4) backup_db ;;
    5) restore_db ;;
    6) restart_services ;;
    7) status_services ;;
    8) logs_bot ;;
    9) logs_app ;;
    10) exit 0 ;;
    *) warn "گزینه نامعتبر" ;;
  esac
done
