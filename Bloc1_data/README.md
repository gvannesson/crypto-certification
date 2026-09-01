# Bloc1 — Data Layer

Collecte, stockage et mise à disposition des données de marché crypto via une API REST.

## Architecture

```
Bloc1_data/
├── src/
│   ├── C1_extraction/     # Extraction depuis APIs externes (Binance, CoinMarketCap)
│   ├── C2_query/          # Requêtes SQL via SQLAlchemy
│   ├── C3_aggregate_ohlcv/ # Agrégation des données OHLCV
│   ├── C4_database/       # Modèles SQLAlchemy + CRUD + alimentation BDD
│   ├── C5_api/            # API FastAPI (routes, auth, dépendances)
│   └── utils/             # Fonctions utilitaires partagées
├── scraping/              # Spider Scrapy (scraping actualités crypto)
│   ├── spiders/           # Spiders (cointelegraph_spider.py)
│   ├── items.py           # Schéma des données scrapées
│   ├── pipelines.py       # Pipeline de déduplication
│   └── settings.py        # Configuration Scrapy
├── tests/                 # Tests pytest
├── config/                # Fichiers YAML de configuration
├── api.Dockerfile         # Image Docker de l'API
├── scripts.Dockerfile     # Image Docker des scripts (cron)
└── entrypoint.sh          # Démarrage du conteneur scripts (init + cron)
```

## Installation

### Prérequis
- Python 3.11+
- PostgreSQL 16
- Docker (recommandé)

### En local
```bash
cd Bloc1_data
uv sync --dev
```

### Via Docker
```bash
docker compose up db data-api data-scripts -d
```

## Base de données

### Schéma principal (PostgreSQL)

| Table | Description |
|-------|-------------|
| `currencies` | Cryptomonnaies et fiats (BTC, ETH, USDT, USD) |
| `trading_pairs` | Paires de trading (BTCUSDT, ETHUSDT, etc.) |
| `exchanges` | Places de marché (Binance) |
| `ohlcv_hourly` | Données OHLCV horaires |
| `ohlcv_daily` | Données OHLCV journalières |
| `predictions_hourly` | Prédictions horaires du modèle ML |
| `predictions_daily` | Prédictions journalières du modèle ML |
| `users` | Utilisateurs de l'API (auth JWT) |
| `cryptocurrency_csv` | Métadonnées des fichiers CSV historiques |
| `csv_historical_data` | Données historiques importées depuis CSV |

### Requêtes SQL — Choix de conception (C2)

Les requêtes utilisent SQLAlchemy ORM avec les optimisations suivantes :

- **Jointures eager** (`joinedload`) sur `TradingPair → Currency` pour éviter le N+1
- **Filtrage par date** avec validation côté API (format YYYY-MM-DD)
- **Tri ascendant** par date pour l'affichage chronologique
- **Contraintes d'unicité** pour éviter les doublons (trading_pair_id + date)
- **Insertion batch** (`bulk_insert_mappings`) avec fallback individuel en cas de conflit

### Algorithme d'agrégation (C3)

L'agrégation des données OHLCV suit ce processus :
1. Extraction des données horaires depuis l'API Binance
2. Regroupement par fenêtre temporelle (1h ou 1j)
3. Calcul : `open` = premier, `high` = max, `low` = min, `close` = dernier, `volume` = somme
4. Insertion en base avec gestion des doublons (contrainte unique)

## API REST

**Port :** 8001 (interne Docker) / 8003 (exposé)  
**Documentation :** http://localhost:8003/docs (OpenAPI/Swagger)

### Endpoints principaux

#### Authentification & Gestion utilisateur

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/v1/authentification/login` | Obtenir un token JWT | Non |
| POST | `/api/v1/authentification/register` | Créer un compte utilisateur | Non |
| GET | `/api/v1/authentification/me` | Profil de l'utilisateur connecté | JWT |
| PUT | `/api/v1/authentification/password` | Modifier son mot de passe | JWT |
| DELETE | `/api/v1/authentification/account` | Supprimer son compte | JWT |

#### Données de marché

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/api/v1/ohlcv/daily_by_trading_pair_id` | Données OHLCV journalières | JWT |
| GET | `/api/v1/ohlcv/hourly_by_trading_pair_id` | Données OHLCV horaires | JWT |
| GET | `/api/v1/trading_pairs/all` | Liste des paires par symbole | JWT |
| GET | `/api/v1/trading_pairs/trading_pair_by_currency_symbols` | Paire par symboles base/quote | JWT |

#### Prédictions (CRUD complet)

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/v1/predictions/hourly` | Créer une prédiction horaire | JWT + script |
| POST | `/api/v1/predictions/daily` | Créer une prédiction journalière | JWT + script |
| GET | `/api/v1/predictions/hourly_by_trading_pair_id/{id}` | Lister les prédictions horaires | JWT |
| GET | `/api/v1/predictions/daily_by_trading_pair_id/{id}` | Lister les prédictions journalières | JWT |
| GET | `/api/v1/predictions/last_hourly_by_trading_pair_id/{id}` | Dernière prédiction horaire | JWT |
| GET | `/api/v1/predictions/last_daily_by_trading_pair_id/{id}` | Dernière prédiction journalière | JWT |
| PUT | `/api/v1/predictions/hourly/{id}` | Modifier une prédiction horaire | JWT + script |
| PUT | `/api/v1/predictions/daily/{id}` | Modifier une prédiction journalière | JWT + script |
| DELETE | `/api/v1/predictions/hourly/{id}` | Supprimer une prédiction horaire | JWT + script |
| DELETE | `/api/v1/predictions/daily/{id}` | Supprimer une prédiction journalière | JWT + script |

#### Monitoring

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/metrics` | Métriques Prometheus | Non |
| GET | `/health` | Healthcheck | Non |

### Authentification
- JWT (python-jose) avec secret configurable
- Hashing bcrypt (passlib) pour les mots de passe
- Expiration configurable (30 min par défaut)
- Rôles : `user` (lecture), `script` (lecture + écriture prédictions)

## Scraping web (C1 — mix de sources)

Spider Scrapy qui scrape les actualités Bitcoin depuis CoinTelegraph.

### Exécution
```bash
cd Bloc1_data
uv run scrapy crawl cointelegraph
```

### Configuration
- **Délai entre requêtes** : 2 secondes (politesse)
- **Respect robots.txt** : oui
- **Déduplication** : par URL (pipeline)
- **Sortie** : `data/scraped_articles.json`

### Données extraites
| Champ | Description |
|-------|-------------|
| `title` | Titre de l'article |
| `date` | Date de publication (YYYY-MM-DD) |
| `url` | URL complète de l'article |
| `category` | Catégorie (News, Markets, Analysis) |

### Sources de données — Récapitulatif

| Source | Méthode | Données |
|--------|---------|---------|
| Binance | API REST | OHLCV (horaire, journalier) |
| CoinMarketCap | API REST | Currencies, paires de trading |
| CryptoDownload | Fichiers CSV | Données historiques |
| CoinTelegraph | **Scraping (Scrapy)** | Actualités BTC |
| PostgreSQL | BDD (SQLAlchemy) | Stockage centralisé |

## Tests

```bash
cd Bloc1_data
uv run pytest tests/ -v --cov=src --cov-report=term-missing
```

## Cron Jobs

| Fréquence | Commande | Description |
|-----------|----------|-------------|
| Toutes les heures (XX:02) | `python -m update_ohlcv --frequency hour` | MAJ données horaires |
| Quotidien (00:01) | `python -m update_ohlcv --frequency day` | MAJ données journalières |
