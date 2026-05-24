#!/usr/bin/env bash
set -euo pipefail
mkdir -p backups
TS=$(date +%F-%H%M)
docker compose exec -T db pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > "backups/db-$TS.sql"
echo "backup saved: backups/db-$TS.sql"
