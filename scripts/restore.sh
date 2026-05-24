#!/usr/bin/env bash
set -euo pipefail
FILE=${1:?"usage: restore.sh <dump.sql>"}
cat "$FILE" | docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
