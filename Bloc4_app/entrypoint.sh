#!/bin/bash
set -e

echo "=== Bloc4 Django App - Starting ==="

echo "Application des migrations..."
python manage.py migrate --noinput

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput

echo "Démarrage de Gunicorn..."
exec gunicorn crypto_app.wsgi:application --bind 0.0.0.0:8080 --workers 3
