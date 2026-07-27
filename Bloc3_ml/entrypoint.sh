#!/bin/bash
set -e

echo "=== Bloc3 ML Pipeline - Starting ==="

echo "Sauvegarde des variables d'environnement pour cron..."
printenv | grep -v "no_proxy" > /etc/environment

echo "Configuration des tâches cron ML..."
CRON_FILE="/etc/cron.d/ml-cron"

echo '05 * * * * root bash -c "source /etc/environment && /usr/local/bin/python /app/update_models_and_predictions.py --granularity hour >> /var/log/cron.log 2>&1"' > $CRON_FILE
echo '03 00 * * * root bash -c "source /etc/environment && /usr/local/bin/python /app/update_models_and_predictions.py --granularity day >> /var/log/cron.log 2>&1"' >> $CRON_FILE

chmod 0644 $CRON_FILE
touch /var/log/cron.log

echo "Tâches cron ML configurées."
echo "Démarrage du service cron..."
exec cron -f
