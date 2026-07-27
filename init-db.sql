-- Crée la base Django si elle n'existe pas déjà
SELECT 'CREATE DATABASE crypto_webapp'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'crypto_webapp')\gexec
