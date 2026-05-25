#!/usr/bin/env bash
set -euo pipefail

REPO_URL="https://github.com/Mhoseinshah1/ZEDPROXYBOT.git"
INSTALL_DIR="/opt/zedproxybot"
BACKUP_DIR="$INSTALL_DIR/backups"

info(){ echo -e "\e[1;36m$1\e[0m"; }
warn(){ echo -e "\e[1;33m$1\e[0m"; }
fail(){ echo -e "\e[1;31m$1\e[0m"; }

compose_cmd(){
  if docker compose version >/dev/null 2>&1; then echo "docker compose"; return 0; fi
  if command -v docker-compose >/dev/null 2>&1; then echo "docker-compose"; return 0; fi
  return 1
}

ensure_deps(){
  info "Checking dependencies..."
  command -v git >/dev/null 2>&1 || { sudo apt-get update -y && sudo apt-get install -y git; }
  if ! command -v docker >/dev/null 2>&1; then
    info "Installing Docker..."
    curl -fsSL https://get.docker.com | sh
    sudo usermod -aG docker "$USER" || true
  fi
  if ! compose_cmd >/dev/null 2>&1; then
    info "Installing docker compose plugin..."
    sudo apt-get update -y && sudo apt-get install -y docker-compose-plugin || true
  fi
  compose_cmd >/dev/null 2>&1 || { fail "Docker Compose is not available."; exit 1; }
}

random_secret(){ openssl rand -hex 32; }

validate_bot_token(){
  local token="$1"
  local out
  out="$(curl -fsS "https://api.telegram.org/bot${token}/getMe" || true)"
  [[ "$out" == *'"ok":true'* ]]
}

load_db_env(){
  DB_USER="zedproxy"; DB_NAME="zedproxy"
  if [[ -f "$INSTALL_DIR/.env" ]]; then
    DB_URL=$(grep '^DATABASE_URL=' "$INSTALL_DIR/.env" | cut -d= -f2- || true)
    if [[ -n "${DB_URL:-}" ]]; then
      DB_USER=$(echo "$DB_URL" | sed -E 's#.*://([^:]+):.*#\1#')
      DB_NAME=$(echo "$DB_URL" | sed -E 's#.*/([^/?]+)$#\1#')
    fi
  fi
}

prompt_env(){
  read -rp "Bot Token: " BOT_TOKEN
  if ! validate_bot_token "$BOT_TOKEN"; then
    fail "Invalid bot token (Telegram getMe failed)."
    exit 1
  fi
  read -rp "Main Admin Telegram ID: " MAIN_ADMIN_ID
  read -rp "Admin username [main_admin]: " ADMIN_USERNAME; ADMIN_USERNAME=${ADMIN_USERNAME:-main_admin}
  read -rsp "Admin password: " ADMIN_PASSWORD; echo
  read -rp "Domain (optional): " DOMAIN
  read -rp "Enable SSL? (yes/no) [no]: " ENABLE_SSL; ENABLE_SSL=${ENABLE_SSL:-no}
  read -rp "Report group chat ID (optional): " REPORT_GROUP_CHAT_ID
  read -rp "Database name [zedproxy]: " DB_NAME; DB_NAME=${DB_NAME:-zedproxy}
  read -rp "Database user [zedproxy]: " DB_USER; DB_USER=${DB_USER:-zedproxy}
  read -rsp "Database password (empty=random): " DB_PASSWORD; echo
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
  info "Environment file created at $INSTALL_DIR/.env"
}

run_migrate_seed(){
  local C; C="$(compose_cmd)"
  (cd "$INSTALL_DIR" && $C up -d --build)
  (cd "$INSTALL_DIR" && $C exec -T app sh -c 'alembic upgrade head || true')
  (cd "$INSTALL_DIR" && $C exec -T app python -m app.db.init_db)
}

health_check(){
  sleep 3
  if curl -fsS http://127.0.0.1:8000/health >/dev/null 2>&1; then
    info "Health check passed."
  else
    warn "Health check failed. Check app logs."
  fi
}

backup_db(){
  [[ -d "$INSTALL_DIR" ]] || { fail "Install directory not found."; return 1; }
  mkdir -p "$BACKUP_DIR"
  load_db_env
  local C; C="$(compose_cmd)"
  local ts file
  ts=$(date +"%Y%m%d_%H%M%S")
  file="$BACKUP_DIR/db_backup_$ts.sql"
  (cd "$INSTALL_DIR" && $C exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > "$file")
  info "Backup created: $file"
}

restore_db(){
  [[ -d "$INSTALL_DIR" ]] || { fail "Install directory not found."; return 1; }
  mkdir -p "$BACKUP_DIR"
  mapfile -t files < <(ls -1 "$BACKUP_DIR"/*.sql 2>/dev/null || true)
  [[ ${#files[@]} -eq 0 ]] && { warn "No backup files found."; return; }
  echo "Available backups:"; for i in "${!files[@]}"; do echo "$((i+1)). ${files[$i]}"; done
  read -rp "Select backup number: " idx
  file="${files[$((idx-1))]:-}"
  [[ -z "$file" ]] && { fail "Invalid selection."; return; }
  read -rp "Confirm restore? (yes/no): " c; [[ "$c" != "yes" ]] && return
  load_db_env
  local C; C="$(compose_cmd)"
  (cd "$INSTALL_DIR" && cat "$file" | $C exec -T db psql -U "$DB_USER" -d "$DB_NAME")
  info "Restore completed."
}

install_bot(){
  ensure_deps
  if [[ ! -d "$INSTALL_DIR/.git" ]]; then
    sudo mkdir -p /opt
    sudo chown -R "$USER":"$USER" /opt
    git clone "$REPO_URL" "$INSTALL_DIR"
  else
    info "Project already exists. Reusing current directory."
  fi
  [[ -f "$INSTALL_DIR/.env" ]] || prompt_env
  run_migrate_seed
  local C; C="$(compose_cmd)"
  (cd "$INSTALL_DIR" && $C ps)
  health_check
}

update_bot(){
  [[ -d "$INSTALL_DIR/.git" ]] || { fail "Project not installed."; return; }
  ensure_deps
  backup_db
  cd "$INSTALL_DIR"
  git checkout main || true
  git fetch origin || { fail "git fetch failed"; return; }
  git pull origin main || { fail "git pull failed"; return; }
  local C; C="$(compose_cmd)"
  $C build
  $C up -d
  $C exec -T app sh -c 'alembic upgrade head || true'
  $C restart app bot
  $C ps
  health_check
  info "Update completed."
}

remove_bot(){
  [[ -d "$INSTALL_DIR" ]] || { warn "Project directory not found."; return; }
  read -rp "Are you sure you want to remove the bot? (yes/no): " c; [[ "$c" != "yes" ]] && return
  warn "Tip: create a backup before full removal."
  local C; C="$(compose_cmd)"
  cd "$INSTALL_DIR"
  $C down || true
  read -rp "Remove volumes as well? (yes/no): " v
  [[ "$v" == "yes" ]] && $C down -v || true
  read -rp "Remove project directory? (yes/no): " d
  [[ "$d" == "yes" ]] && rm -rf "$INSTALL_DIR"
  info "Removal completed."
}

restart_services(){ local C; C="$(compose_cmd)"; cd "$INSTALL_DIR"; $C restart app bot; $C ps; }
status_services(){ local C; C="$(compose_cmd)"; cd "$INSTALL_DIR"; $C ps; }
logs_bot(){ local C; C="$(compose_cmd)"; cd "$INSTALL_DIR"; $C logs -f bot; }
logs_app(){ local C; C="$(compose_cmd)"; cd "$INSTALL_DIR"; $C logs -f app; }

while true; do
  echo
  info "ZedProxyBot Manager"
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
    1) install_bot ;;
    2) update_bot ;;
    3) remove_bot ;;
    4) backup_db ;;
    5) restore_db ;;
    6) restart_services ;;
    7) status_services ;;
    8) logs_bot ;;
    9) logs_app ;;
    10) exit 0 ;;
    *) warn "Invalid option" ;;
  esac
done
