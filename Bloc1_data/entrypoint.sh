#!/bin/bash
set -e

echo "=== Bloc1 Data Scripts - Starting ==="

mkdir -p /app/data/logs

LOCK_FILE="/app/data/logs/.init_done"

if [ ! -f "$LOCK_FILE" ]; then
    echo "First run: initializing database and loading historical data..."
    python -m init_db_and_data
    touch "$LOCK_FILE"
    echo "Initialization complete."
else
    echo "Database already initialized, skipping init."
fi

echo "Sauvegarde des variables d'environnement pour cron..."
printenv | grep -v "no_proxy" > /etc/environment

echo "Setting up cron jobs..."
cat <<CRON > /etc/cron.d/ohlcv-update
02 * * * * root bash -c "source /etc/environment && cd /app && /app/.venv/bin/python -m update_ohlcv --frequency hour >> /app/data/logs/cron_hourly.log 2>&1"
01 0 * * * root bash -c "source /etc/environment && cd /app && /app/.venv/bin/python -m update_ohlcv --frequency day >> /app/data/logs/cron_daily.log 2>&1"
CRON

chmod 0644 /etc/cron.d/ohlcv-update
crontab /etc/cron.d/ohlcv-update

echo "Starting cron daemon..."
cron -f
