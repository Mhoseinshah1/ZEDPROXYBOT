#!/usr/bin/env bash
set -e
FILE="$1"
docker compose exec -T db psql -U zedproxy zedproxy < "$FILE"
