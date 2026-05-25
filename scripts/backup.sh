#!/usr/bin/env bash
set -e
mkdir -p backups
docker compose exec -T db pg_dump -U zedproxy zedproxy > backups/backup_$(date +%F_%H%M).sql
echo done
