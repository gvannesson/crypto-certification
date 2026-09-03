# Cahier des Charges — Classification de Tendance Crypto

## Table des matières

1. [Présentation du projet](#1-présentation-du-projet)
2. [Architecture globale](#2-architecture-globale)
3. [Arborescence du projet](#3-arborescence-du-projet)
4. [Bloc1 — Couche données (Data Layer)](#4-bloc1--couche-données-data-layer)
5. [Bloc2 — Veille technologique](#5-bloc2--veille-technologique)
6. [Bloc3 — Couche Machine Learning](#6-bloc3--couche-machine-learning)
7. [Bloc4 — Application web (Django)](#7-bloc4--application-web-django)
8. [Déploiement Docker](#8-déploiement-docker)
9. [Variables d'environnement](#9-variables-denvironnement)
10. [Tests](#10-tests)
11. [Annexes techniques](#11-annexes-techniques)

---

## 1. Présentation du projet

### 1.1 Objectif

Construire une plateforme complète de **classification de tendance** pour les cryptomonnaies. Le système prédit, pour chaque pas de temps (heure ou jour), si le prix va **monter (UP)**, **descendre (DOWN)** ou **rester stable (STABLE)**.

C'est un problème de **classification supervisée à 3 classes**, contrairement à un problème de régression qui prédirait le prix exact.

### 1.2 Paires de trading suivies

| Paire | Base | Quote | Granularités |
|-------|------|-------|-------------|
| BTC-USD | Bitcoin | US Dollar | horaire, journalière |
| BTC-USDT | Bitcoin | Tether USDt | horaire, journalière |

### 1.3 Stack technique

| Couche | Technologie |
|--------|-------------|
| APIs internes (Bloc1 data, Bloc3 ML) | Python, FastAPI, Uvicorn |
| Application web (Bloc4) | Python, Django |
| Base de données | PostgreSQL, SQLAlchemy (Bloc1/Bloc3), Django ORM (Bloc4) |
| Machine Learning | scikit-learn (XGBoost, Random Forest, LogisticRegression), pandas, numpy |
| Indicateurs techniques | pandas-ta ou ta-lib |
| MLOps | MLflow |
| Conteneurisation | Docker, docker-compose |
| Tests | pytest, pytest-cov |

### 1.4 Définition de la variable cible

La cible est construite à partir de la variation relative du prix de clôture entre deux pas de temps consécutifs :

```
variation = (close[t] - close[t-1]) / close[t-1]
```

La classification ternaire utilise un seuil configurable (par défaut `0.5%` soit `0.005`) :

| Classe | Condition | Label encodé |
|--------|-----------|-------------|
| **UP** | `variation > +seuil` | 2 |
| **STABLE** | `-seuil <= variation <= +seuil` | 1 |
| **DOWN** | `variation < -seuil` | 0 |

Le seuil doit être configurable dans un fichier YAML pour pouvoir être ajusté sans modifier le code.

---

## 2. Architecture globale

Le projet est découpé en **4 couches indépendantes** communiquant via des APIs REST et une base de données PostgreSQL partagée.

```
┌──────────────────────────────────────────────────────────────────────┐
│  SOURCES EXTERNES                                                     │
│  • Binance API (OHLCV)   • CoinMarketCap (référentiels)              │
│  • CryptoDownload (CSV historiques)   • Token Metrics (signaux)       │
└──────────────────────────────────────────────────────────────────────┘
        │                           │
        │ HTTP / REST               │ HTTP / REST
        ▼                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Bloc1 — DATA LAYER                                                      │
│  ┌─────────────────┐    ┌───────────────────────────────────────┐     │
│  │  data-scripts    │    │  data-api (FastAPI :8001)              │     │
│  │  (cron)          │───▶│  /ohlcv, /predictions, /trading_pairs │     │
│  │  • init BDD      │    │  /authentification                    │     │
│  │  • update OHLCV  │    └───────────────────────────────────────┘     │
│  └─────────────────┘              │                                    │
│          │                        │                                    │
│          ▼                        ▼                                    │
│  ┌──────────────────────────────────────────┐                         │
│  │  PostgreSQL                               │                         │
│  │  currencies, trading_pairs, exchanges     │                         │
│  │  ohlcv_hourly, ohlcv_daily                │                         │
│  │  predictions_hourly, predictions_daily    │                         │
│  │  users                                    │                         │
│  └──────────────────────────────────────────┘                         │
└──────────────────────────────────────────────────────────────────────┘
        │ GET OHLCV (JWT)           ▲ POST predictions (JWT)
        ▼                           │
┌──────────────────────────────────────────────────────────────────────┐
│  Bloc3 — ML LAYER                                                        │
│  ┌─────────────────┐    ┌────────────────────────────────────────┐    │
│  │  ml-pipeline     │    │  ml-api (FastAPI :8002)                │    │
│  │  (cron)          │    │  /classify_hourly, /classify_daily     │    │
│  │  • fetch OHLCV   │    └────────────────────────────────────────┘    │
│  │  • indicateurs   │              │                                   │
│  │  • train models  │    ┌────────────────────────────────────────┐    │
│  │  • classify      │    │  MLflow (:5000)                        │    │
│  │  • POST results  │    │  Tracking des expériences              │    │
│  └─────────────────┘    └────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────────────┘
        │ HTTP                      │ HTTP
        ▼                           ▼
┌──────────────────────────────────────────────────────────────────────┐
│  Bloc4 — APPLICATION WEB (Django :8080)                                  │
│  • Authentification (Django auth native)                               │
│  • Dashboard : dernières prédictions, statistiques de performance      │
│  • Page de classification à la demande (formulaire → ml-api)          │
│  • Graphiques : bougies OHLCV + prédictions historiques colorées      │
└──────────────────────────────────────────────────────────────────────┘
```

### Flux de données principal

1. `data-scripts` extrait les données OHLCV depuis Binance/CryptoDownload et les stocke dans PostgreSQL
2. `data-api` expose ces données via une API REST sécurisée par JWT
3. `ml-pipeline` (cron) récupère les OHLCV via `data-api`, calcule les indicateurs techniques, entraîne/évalue les modèles, produit des prédictions de classe (UP/DOWN/STABLE), et les renvoie à `data-api` pour stockage
4. `ml-api` permet de faire des prédictions à la demande en chargeant les modèles entraînés
5. `webapp` (Django) affiche le dashboard, les graphiques et les prédictions à l'utilisateur

---

## 3. Arborescence du projet

```
classification-tendance-crypto/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt                    # Dépendances consolidées (dev)
├── README.md
│
├── docs/
│   └── (documentation, schémas)
│
├── Bloc1_data/                            # Couche données
│   ├── init_db_and_data.py            # Script d'initialisation BDD + ETL
│   ├── update_ohlcv.py                # Script de mise à jour incrémentale
│   ├── entrypoint.sh                  # Point d'entrée Docker (init + cron)
│   ├── api.Dockerfile
│   ├── scripts.Dockerfile
│   ├── requirements.txt
│   ├── config/
│   │   ├── extract_config.yaml        # URLs sources, paires, années de départ
│   │   └── update_config.yaml         # URL Binance, paires pour update
│   └── src/
│       ├── settings.py                # Chargement YAML + variables d'env
│       ├── utils/
│       │   └── functions.py           # Fonctions utilitaires
│       ├── extraction/                # Extraction depuis les sources
│       │   ├── extract_coinmarketcap.py
│       │   ├── extract_cryptodownload.py
│       │   ├── extract_csv_data.py
│       │   └── extract_binance_data.py
│       ├── query/                     # Fonctions de requête BDD
│       │   ├── query_currencies.py
│       │   ├── query_trading_pairs.py
│       │   ├── query_ohlcv_hourly.py
│       │   ├── query_ohlcv_daily.py
│       │   └── query_predictions.py
│       ├── aggregate/
│       │   └── aggregate_ohlcv.py     # Agrégation minute→heure→jour
│       ├── database/
│       │   ├── database.py            # Engine SQLAlchemy, sessions
│       │   ├── models.py             # Modèles ORM
│       │   ├── crud.py               # Opérations CRUD génériques
│       │   └── feed_db/              # Scripts d'alimentation
│       │       ├── feed_currencies.py
│       │       ├── feed_trading_pairs.py
│       │       └── feed_ohlcv_data.py
│       └── api/
│           ├── api.py                 # App FastAPI
│           ├── routes/
│           │   ├── login.py           # /authentification/login, /register
│           │   ├── ohlcv.py           # /ohlcv/hourly_*, /ohlcv/daily_*
│           │   ├── trading_pairs.py   # /trading_pairs/*
│           │   └── predictions.py     # /predictions/hourly_*, /predictions/daily_*
│           └── utils/
│               ├── auth.py            # JWT creation/validation
│               ├── deps.py            # Dependencies injection (get_current_user)
│               └── classes.py         # Pydantic models (request/response)
│
├── Bloc2_veille/                          # Veille technologique
│   ├── parametrage.py                 # Script Token Metrics
│   ├── requirements.txt
│   └── README.md
│
├── Bloc3_ml/                              # Couche Machine Learning
│   ├── update_models_and_predictions.py  # Pipeline principal
│   ├── entrypoint.sh                    # Cron pour le pipeline
│   ├── pipeline.Dockerfile
│   ├── api.Dockerfile
│   ├── mlflow.Dockerfile
│   ├── requirements.txt
│   ├── config/
│   │   ├── data_config.yaml           # Endpoints Bloc1 API
│   │   ├── ml_config.yaml             # Configs modèles, seuils, dates
│   │   ├── hour_models_config.yaml    # Config par paire (horaire)
│   │   └── day_models_config.yaml     # Config par paire (journalier)
│   └── src/
│       ├── settings.py
│       ├── utils/
│       │   ├── classes.py             # TradingPairClassifier
│       │   └── functions.py
│       ├── data/
│       │   ├── fetch_data.py          # Récupère OHLCV depuis Bloc1 API
│       │   └── send_data.py           # Envoie les prédictions à Bloc1 API
│       ├── features/
│       │   └── build_features.py      # Calcul indicateurs techniques + cible
│       ├── model/
│       │   ├── initiate_classifier.py # Initialise les classifieurs par paire
│       │   ├── train_model.py         # Entraîne le modèle
│       │   ├── predict_model.py       # Produit les prédictions
│       │   ├── evaluate_model.py      # Calcul des métriques
│       │   └── save_model.py          # Sauvegarde pickle/joblib
│       ├── api/
│       │   ├── api.py                 # FastAPI pour prédictions à la demande
│       │   ├── routes/
│       │   │   ├── classify.py
│       │   │   └── login.py
│       │   └── utils/
│       │       ├── auth.py
│       │       ├── deps.py
│       │       ├── classes.py
│       │       └── functions.py       # Chargement modèles, feature engineering
│       ├── monitoring/
│       │   └── monitor_training.py    # Logging MLflow
│       └── tests/
│           └── ...
│
└── Bloc4_app/                             # Application Web Django
    ├── manage.py
    ├── app.Dockerfile
    ├── requirements.txt
    ├── crypto_app/                     # Projet Django
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── accounts/                       # App Django : authentification
    │   ├── models.py                  # (utilise User Django natif)
    │   ├── views.py                   # login, register, logout
    │   ├── urls.py
    │   ├── forms.py                   # LoginForm, RegisterForm
    │   └── templates/accounts/
    │       ├── login.html
    │       └── register.html
    ├── dashboard/                      # App Django : dashboard principal
    │   ├── views.py                   # Vue dashboard, statistiques
    │   ├── urls.py
    │   ├── services.py                # Appels vers data-api (OHLCV, prédictions)
    │   └── templates/dashboard/
    │       ├── index.html
    │       └── charts.html
    ├── forecast/                       # App Django : classification à la demande
    │   ├── views.py                   # Formulaire + appel ml-api
    │   ├── urls.py
    │   ├── forms.py                   # ClassifyForm
    │   ├── services.py                # Appels vers ml-api
    │   └── templates/forecast/
    │       └── classify.html
    ├── templates/                       # Templates globaux
    │   └── base.html                  # Layout commun (navbar, footer, CSS)
    ├── static/
    │   ├── css/
    │   ├── js/
    │   └── img/
    └── tests/
        ├── test_views.py
        └── test_services.py
```

---

## 4. Bloc1 — Couche données (Data Layer)

### 4.1 Sources de données

#### 4.1.1 CoinMarketCap (initialisation uniquement)

Récupère les référentiels de base (liste de cryptomonnaies, devises fiat, exchanges) via l'API CoinMarketCap.

| Endpoint | Données récupérées |
|----------|-------------------|
| `/v1/cryptocurrency/map` | id, name, symbol, slug, rank pour chaque crypto |
| `/v1/fiat/map` | id, name, symbol, sign pour chaque fiat |
| `/v1/exchange/map` | id, name, slug pour chaque exchange |

Ces données alimentent les tables `currencies` et `exchanges`.

Nécessite une clé API CoinMarketCap (plan gratuit suffisant).

#### 4.1.2 CryptoDownload (initialisation uniquement)

Récupère des CSV historiques OHLCV depuis [CryptoDataDownload](https://www.cryptodatadownload.com/) pour différents exchanges (Binance, Gemini, Bitstamp).

Pour chaque paire de trading configurée, le script :
1. Télécharge le JSON listant les CSV disponibles
2. Filtre les CSV correspondant aux paires recherchées (BTC-USD, BTC-USDT)
3. Télécharge chaque CSV et alimente les tables `cryptocurrency_csv` et `csv_historical_data`

Les données CSV sont ensuite agrégées dans les tables OHLCV par granularité.

#### 4.1.3 Binance API (mise à jour récurrente)

Endpoint : `https://api.binance.com/api/v3/klines`

Récupère les bougies OHLCV incrémentalement. Le script :
1. Interroge la BDD pour trouver la dernière entrée connue pour chaque paire
2. Requête Binance à partir du timestamp suivant
3. Pagine par blocs de 500 (limite Binance)
4. Filtre les bougies non clôturées (date < maintenant arrondi)
5. Sauvegarde dans `ohlcv_hourly` ou `ohlcv_daily`

Colonnes récupérées par bougie :

| Champ | Type | Description |
|-------|------|-------------|
| date | datetime | Timestamp d'ouverture de la bougie |
| open | float | Prix d'ouverture |
| high | float | Prix le plus haut |
| low | float | Prix le plus bas |
| close | float | Prix de clôture |
| volume_quote | float | Volume en devise de cotation |

Aucune clé API n'est nécessaire (endpoint public).

### 4.2 Configuration YAML

#### extract_config.yaml

```yaml
save_dir:
  cryptodownload: "data/external/cryptodownload"
  coinmarketcap: "data/external/coinmarketcap"

cryptodownload:
  json_urls:
    binance_h_m: "https://api.cryptodatadownload.com/v1/data/ohlc/binance/guest/spot/available?_=1740047643800&format=json"
    binance_d: "https://api.cryptodatadownload.com/v1/data/ohlc/binance/available?_=1752854076487&format=json"
    gemini_m: "https://api.cryptodatadownload.com/v1/data/ohlc/gemini/guest/available?_=1740057730875&format=json"
    gemini_h_d: "https://api.cryptodatadownload.com/v1/data/ohlc/gemini/available?_=1752940667446&format=json"
    bitstamp_m: "https://api.cryptodatadownload.com/v1/data/ohlc/bitstamp/guest/spot/available?_=1740058272110&format=json"
    bitstamp_h_d: "https://api.cryptodatadownload.com/v1/data/ohlc/bitstamp/available?_=1752940695157&format=json"

coinmarketcap:
  maps:
    cryptocurrency_map: "https://pro-api.coinmarketcap.com/v1/cryptocurrency/map"
    fiat_map: "https://pro-api.coinmarketcap.com/v1/fiat/map"
    exchange_map: "https://pro-api.coinmarketcap.com/v1/exchange/map"

trading_pairs:
  - base_name: "Bitcoin"
    quote_name: "United States Dollar"
    timeframes: ["hour", "day"]
    from_year: 2020
  - base_name: "Bitcoin"
    quote_name: "Tether USDt"
    timeframes: ["hour", "day"]
    from_year: 2020
```

#### update_config.yaml

```yaml
binance_ohlcv_url: "https://api.binance.com/api/v3/klines"

trading_pairs:
  - base_name: "Bitcoin"
    quote_name: "Tether USDt"
    timeframes: ["hour", "day"]
  - base_name: "Bitcoin"
    quote_name: "United States Dollar"
    timeframes: ["hour", "day"]
```

### 4.3 Modèles de données (SQLAlchemy)

#### Table `currencies`

| Colonne | Type | Contrainte |
|---------|------|-----------|
| id | Integer | PK (vient de CoinMarketCap) |
| name | String | NOT NULL |
| symbol | String | NOT NULL |
| slug | String | nullable |
| sign | String | nullable |
| rank | Integer | nullable |
| rank_date | DateTime | nullable |
| type | String | NOT NULL ("crypto" ou "fiat") |

Contrainte unique : `(name, symbol, rank, type)`

#### Table `trading_pairs`

| Colonne | Type | Contrainte |
|---------|------|-----------|
| id | Integer | PK auto-incrémenté |
| base_currency_id | Integer | FK → currencies.id, NOT NULL |
| quote_currency_id | Integer | FK → currencies.id, NOT NULL |

Contrainte unique : `(base_currency_id, quote_currency_id)`

#### Table `exchanges`

| Colonne | Type | Contrainte |
|---------|------|-----------|
| id | Integer | PK (vient de CoinMarketCap) |
| name | String | NOT NULL |
| slug | String | NOT NULL |

Contrainte unique : `(name, slug)`

#### Table `ohlcv_hourly` (et `ohlcv_daily` avec même schéma)

| Colonne | Type | Contrainte |
|---------|------|-----------|
| id | Integer | PK auto-incrémenté |
| trading_pair_id | Integer | FK → trading_pairs.id, NOT NULL |
| date | DateTime | NOT NULL |
| open | Float | NOT NULL |
| high | Float | NOT NULL |
| low | Float | NOT NULL |
| close | Float | NOT NULL |
| volume_quote | Float | NOT NULL |

Contrainte unique : `(trading_pair_id, date)`

#### Table `predictions_hourly` (et `predictions_daily` avec même schéma)

| Colonne | Type | Contrainte |
|---------|------|-----------|
| id | Integer | PK auto-incrémenté |
| trading_pair_id | Integer | FK → trading_pairs.id, NOT NULL |
| date | DateTime | NOT NULL |
| predicted_class | Integer | NOT NULL (0=DOWN, 1=STABLE, 2=UP) |
| predicted_label | String | NOT NULL ("DOWN", "STABLE", "UP") |
| confidence | Float | nullable (probabilité max du modèle) |
| model_name | String | nullable |

Contrainte unique : `(trading_pair_id, date)`

#### Table `users`

| Colonne | Type | Contrainte |
|---------|------|-----------|
| id | Integer | PK auto-incrémenté |
| username | String | UNIQUE, NOT NULL |
| password_hashed | String | NOT NULL |
| status | String | NOT NULL, default "active" |
| role | String | NOT NULL, default "user" |

### 4.4 Script d'initialisation (`init_db_and_data.py`)

Ce script s'exécute une seule fois au premier lancement (protégé par un fichier de verrouillage). Il fait dans l'ordre :

1. Créer toutes les tables via `Base.metadata.create_all(engine)`
2. Extraire les données CoinMarketCap → alimenter `currencies` et `exchanges`
3. Créer les `trading_pairs` configurées (à partir des noms base/quote)
4. Extraire les CSV CryptoDownload → alimenter `cryptocurrency_csv` et `csv_historical_data`
5. Agréger les données CSV en `ohlcv_hourly` et `ohlcv_daily`
6. Créer l'utilisateur script (pour l'authentification inter-services)

### 4.5 Script de mise à jour (`update_ohlcv.py`)

Accepte un argument `--frequency` (`hour` ou `day`). Pour chaque paire configurée ayant cette fréquence :
1. Récupère la dernière entrée OHLCV en BDD pour cette paire
2. Appelle `fetch_binance_data()` pour récupérer les données depuis ce point
3. Sauvegarde les nouvelles entrées

### 4.6 Cron (entrypoint.sh)

```
02 * * * *  → update_ohlcv.py --frequency hour   (toutes les heures à :02)
01 00 * * * → update_ohlcv.py --frequency day    (tous les jours à 00:01)
```

### 4.7 API REST (FastAPI, port 8001)

Préfixe : `/api/v1`

#### Authentification

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| POST | `/authentification/login` | Retourne un JWT (username + password en form-data) |
| POST | `/authentification/register` | Crée un utilisateur (username + password) |

JWT : signé avec `API_E1_SECRET_KEY`, algorithme configurable (HS256 par défaut).

#### Trading Pairs

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/trading_pairs/all` | Liste toutes les paires |
| GET | `/trading_pairs/trading_pair_by_currency_symbols?base=BTC&quote=USDT` | Récupère une paire par symboles |

#### OHLCV

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/ohlcv/hourly_by_trading_pair_id?trading_pair_id=X` | OHLCV horaire pour une paire |
| GET | `/ohlcv/daily_by_trading_pair_id?trading_pair_id=X` | OHLCV journalier pour une paire |

#### Prédictions

| Méthode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/predictions/hourly_by_trading_pair_id?trading_pair_id=X` | Prédictions horaires |
| GET | `/predictions/daily_by_trading_pair_id?trading_pair_id=X` | Prédictions journalières |
| POST | `/predictions/hourly` | Enregistre des prédictions horaires (utilisé par ml-pipeline) |
| POST | `/predictions/daily` | Enregistre des prédictions journalières (utilisé par ml-pipeline) |

Tous les endpoints (sauf login/register) nécessitent un header `Authorization: Bearer <JWT>`.

---

## 5. Bloc2 — Veille technologique

### 5.1 Objectif

Script standalone (non intégré dans Docker) qui appelle l'API **Token Metrics** pour récupérer des signaux de trading. Sert à illustrer la capacité de veille et d'analyse de sources externes.

### 5.2 Implémentation

Fichier : `Bloc2_veille/parametrage.py`

- Charge la clé API depuis `.env` (variable `TOKEN_METRICS_API_KEY`)
- Appelle l'endpoint `https://api.tokenmetrics.com/v2/trading-signals`
- Construit un DataFrame pandas avec les colonnes :
  - `TOKEN_NAME`, `TOKEN_SYMBOL`, `DATE`
  - `TRADING_SIGNAL` (signal d'achat/vente)
  - `TOKEN_TREND` (tendance du token)
  - `TRADING_SIGNALS_RETURNS`, `HOLDING_RETURNS` (rendements)
- Affiche les résultats dans la console

### 5.3 Dépendances

```
pandas
requests
python-dotenv
```

### 5.4 Documentation

Un `README.md` dans `Bloc2_veille/` doit expliquer :
- Ce qu'est Token Metrics
- Comment obtenir une clé API
- Comment interpréter les signaux
- La comparaison avec d'autres solutions (CoinGecko, Messari, LunarCrush)

---

## 6. Bloc3 — Couche Machine Learning

### 6.1 Objectif

Entraîner et comparer plusieurs modèles de classification pour prédire la tendance (UP/DOWN/STABLE) du prix de clôture à la prochaine bougie (horizon 1).

### 6.2 Modèles à comparer

| Modèle | Module scikit-learn | Rôle |
|--------|-------------------|------|
| XGBoost | `xgboost.XGBClassifier` | Modèle principal, bon sur données tabulaires |
| Random Forest | `sklearn.ensemble.RandomForestClassifier` | Modèle d'ensemble, benchmark robuste |
| Logistic Regression | `sklearn.linear_model.LogisticRegression` | Baseline simple pour comparaison |

Le modèle utilisé par paire est configurable dans les fichiers YAML. MLflow sert à tracer tous les modèles et à identifier le meilleur.

### 6.3 Feature Engineering (`features/build_features.py`)

À partir des données OHLCV brutes, construire les features suivantes :

#### 6.3.1 Lags autorégressifs

Pour les colonnes `close`, `volume_quote`, `high`, `low` :
- Horaire : 24 lags (t-1 à t-24)
- Journalier : 7 lags (t-1 à t-7)

#### 6.3.2 Rendements (returns)

```python
df["return_1"] = df["close"].pct_change(1)
df["return_3"] = df["close"].pct_change(3)
df["return_6"] = df["close"].pct_change(6)
df["return_12"] = df["close"].pct_change(12)  # horaire uniquement
```

#### 6.3.3 Indicateurs techniques

Utiliser la librairie `pandas-ta` (ou calculer manuellement) :

| Indicateur | Paramètres | Description |
|-----------|-----------|-------------|
| **RSI** (Relative Strength Index) | period=14 | Force relative du mouvement. RSI > 70 = surachat, RSI < 30 = survente |
| **MACD** (Moving Average Convergence Divergence) | fast=12, slow=26, signal=9 | Croisement de moyennes mobiles. Produit 3 colonnes : macd, macd_signal, macd_hist |
| **Bollinger Bands** | period=20, std=2 | Bandes de volatilité autour d'une SMA. Produit : bb_upper, bb_middle, bb_lower |
| **SMA** (Simple Moving Average) | periods=[7, 14, 50] | Moyennes mobiles simples |
| **EMA** (Exponential Moving Average) | periods=[12, 26] | Moyennes mobiles exponentielles |
| **ATR** (Average True Range) | period=14 | Mesure de la volatilité |

#### 6.3.4 Encodeurs temporels

Extraire du timestamp :
- `hour` (0-23) — horaire uniquement
- `day_of_week` (0-6)
- `day_of_month` (1-31)
- `month` (1-12)
- `is_weekend` (0 ou 1)

#### 6.3.5 Variable cible

```python
SEUIL = 0.005  # configurable dans ml_config.yaml

df["variation"] = df["close"].pct_change(1)
df["target"] = pd.cut(
    df["variation"],
    bins=[-float("inf"), -SEUIL, SEUIL, float("inf")],
    labels=[0, 1, 2]  # 0=DOWN, 1=STABLE, 2=UP
).astype(int)
```

Supprimer les lignes avec des NaN (premières lignes dues aux lags/indicateurs).

### 6.4 Configuration YAML

#### ml_config.yaml

```yaml
models_config:
  xgboost:
    module: "xgboost"
    class: "XGBClassifier"
    default_params:
      n_estimators: 200
      max_depth: 6
      learning_rate: 0.1
      objective: "multi:softprob"
      num_class: 3
      eval_metric: "mlogloss"
      use_label_encoder: false
  random_forest:
    module: "sklearn.ensemble"
    class: "RandomForestClassifier"
    default_params:
      n_estimators: 200
      max_depth: 10
      random_state: 42
      class_weight: "balanced"
  logistic_regression:
    module: "sklearn.linear_model"
    class: "LogisticRegression"
    default_params:
      max_iter: 1000
      multi_class: "multinomial"
      solver: "lbfgs"
      class_weight: "balanced"

classification:
  seuil: 0.005
  labels: {0: "DOWN", 1: "STABLE", 2: "UP"}

dates_by_granularity:
  daily:
    training_start: "2020-01-01"
    training_end: "2024-12-31"
    test_start: "2025-01-01"
    test_end: "2025-05-31"
  hourly:
    training_start: "2024-01-01"
    training_end: "2024-12-31"
    test_start: "2025-01-01"
    test_end: "2025-03-31"
```

#### hour_models_config.yaml

```yaml
pair_models:
  - id: <id_trading_pair>
    symbol: "BTC-USDT"
    base_currency: "BTC"
    quote_currency: "USDT"
    granularity_type: "hourly"
    model: "xgboost"
    feature_lags: 24
    params:
      n_estimators: 200
      max_depth: 6
      learning_rate: 0.1
  - id: <id_trading_pair>
    symbol: "BTC-USD"
    base_currency: "BTC"
    quote_currency: "USD"
    granularity_type: "hourly"
    model: "xgboost"
    feature_lags: 24
    params:
      n_estimators: 200
      max_depth: 6
      learning_rate: 0.1
```

#### day_models_config.yaml

Même structure avec `granularity_type: "daily"` et `feature_lags: 7`.

### 6.5 Classe `TradingPairClassifier` (`utils/classes.py`)

```python
class TradingPairClassifier:
    def __init__(self, pair_model_info):
        self.trading_pair_id = pair_model_info["id"]
        self.symbol = pair_model_info["symbol"]
        self.base_currency = pair_model_info["base_currency"]
        self.quote_currency = pair_model_info["quote_currency"]
        self.granularity_type = pair_model_info["granularity_type"]
        self.model_name = pair_model_info["model"]
        self.model_params = pair_model_info.get("params", {})
        self.feature_lags = pair_model_info.get("feature_lags", 24)
        self.model_instance = self._initialize_model()

        # DataFrames pour stocker les résultats
        self.df_historical_data = None      # OHLCV brut
        self.df_features = None             # Features calculées
        self.historical_predictions = pd.DataFrame()  # Prédictions historiques (test)
        self.current_predictions = pd.DataFrame()     # Prédictions courantes

        # Paramètres selon granularité
        if self.granularity_type == "daily":
            self.test_window = 7
            self.test_period_duration = pd.DateOffset(months=6)
        elif self.granularity_type == "hourly":
            self.test_window = 24
            self.test_period_duration = pd.DateOffset(months=1)

    def _initialize_model(self):
        """Instancie dynamiquement le modèle à partir de la config."""
        module = importlib.import_module(models_config[self.model_name]["module"])
        ModelClass = getattr(module, models_config[self.model_name]["class"])
        params = {**models_config[self.model_name]["default_params"], **self.model_params}
        return ModelClass(**params)
```

### 6.6 Pipeline principal (`update_models_and_predictions.py`)

Accepte un argument `--granularity` (`hour` ou `day`).

Étapes dans l'ordre :

```
1. initialize_pair_classifiers_by_granularity(granularity)
   → Crée un TradingPairClassifier par paire configurée
   → Récupère les OHLCV depuis data-api (JWT)
   → Calcule les features (indicateurs techniques + lags + cible)

2. monitor_trainings(pair_classifiers, granularity)
   → Pour chaque classifier :
     → Découpe en périodes de test glissantes
     → Entraîne le modèle sur train, prédit sur test
     → Calcule accuracy, F1 (macro), matrice de confusion
     → Log tout dans MLflow

3. make_predictions(pair_classifiers)
   → Pour chaque classifier :
     → Entraîne le modèle sur toutes les données connues
     → Prédit la classe pour la prochaine bougie
     → Stocke predicted_class, predicted_label, confidence

4. save_predictions_to_db(pair_classifiers)
   → POST les prédictions vers data-api (/predictions/hourly ou /predictions/daily)

5. save_classifiers_models(pair_classifiers, granularity)
   → Sauvegarde chaque modèle entraîné en pickle/joblib
   → Fichier : {granularity}_models/{SYMBOL}.pkl
```

### 6.7 Métriques d'évaluation

| Métrique | Description | Utilité |
|----------|-------------|---------|
| **Accuracy** | % de prédictions correctes | Vue globale |
| **F1 Score (macro)** | Moyenne harmonique precision/recall, pondérée par classe | Gère le déséquilibre des classes |
| **F1 Score (par classe)** | F1 pour UP, DOWN, STABLE séparément | Identifie les faiblesses par classe |
| **Matrice de confusion** | Tableau classes réelles vs prédites | Analyse fine des erreurs |
| **Classification Report** | precision, recall, f1, support par classe | Vue détaillée |
| **Direction Accuracy** | % de bonnes prédictions UP vs DOWN (excluant STABLE) | Métrique métier clé |

Toutes sont loggées dans MLflow avec les tags : `symbol`, `model_name`, `granularity`, `training_date`.

### 6.8 Cron ML (entrypoint.sh)

```
05 * * * *  → update_models_and_predictions.py --granularity hour  (à :05)
03 00 * * * → update_models_and_predictions.py --granularity day   (à 00:03)
```

Le décalage de 3-5 minutes par rapport au cron Bloc1 garantit que les données OHLCV sont déjà à jour.

### 6.9 API ML (FastAPI, port 8002)

Préfixe : `/api/v1`

| Méthode | Endpoint | Corps (JSON) | Réponse |
|---------|----------|-------------|---------|
| POST | `/authentification/login` | `{username, password}` | JWT |
| POST | `/classify/classify_hourly` | `{trading_pair_symbol, num_pred}` | `{predictions: [{date, class, label, confidence}]}` |
| POST | `/classify/classify_daily` | `{trading_pair_symbol, num_pred}` | idem |

Pour les prédictions à la demande :
1. Charger le modèle pickle correspondant
2. Récupérer les dernières données OHLCV (suffisamment pour calculer les indicateurs)
3. Calculer les features
4. Prédire avec `model.predict()` et `model.predict_proba()`
5. Retourner la classe, le label et la probabilité la plus élevée (confidence)

`num_pred` est limité à 1-24 pour horaire et 1-7 pour journalier.

### 6.10 MLflow (port 5000)

Serveur MLflow pour tracker les expériences.

- Un experiment par paire : `{SYMBOL}_training_monitoring`
- Un run par exécution du cron, nommé `{granularity}_{training_date}`
- Tags : symbol, model_name, granularity
- Paramètres : model_params, training_date, test_period_duration, seuil_classification
- Métriques : accuracy, f1_macro, f1_up, f1_down, f1_stable, direction_accuracy

Dockerfile MLflow :

```dockerfile
FROM python:3.11-slim
RUN pip install mlflow
WORKDIR /app
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000", "--backend-store-uri", "file:///app/mlruns"]
```

---

## 7. Bloc4 — Application web (Django)

### 7.1 Structure du projet Django

Le projet Django s'appelle `crypto_app` et contient 3 apps :

| App | Responsabilité |
|-----|---------------|
| `accounts` | Authentification (login, register, logout) via Django auth native |
| `dashboard` | Dashboard principal avec graphiques et statistiques |
| `forecast` | Classification à la demande via formulaire |

### 7.2 App `accounts`

Utilise le système d'authentification natif de Django (`django.contrib.auth`).

#### Views

| URL | View | Méthode | Description |
|-----|------|---------|-------------|
| `/` | `index` | GET | Page d'accueil, redirige vers dashboard si connecté |
| `/login/` | `login_view` | GET/POST | Formulaire de connexion Django |
| `/register/` | `register_view` | GET/POST | Formulaire d'inscription |
| `/logout/` | `logout_view` | GET | Déconnexion |

#### Formulaires

```python
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

class LoginForm(AuthenticationForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={"placeholder": "Nom d'utilisateur"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Mot de passe"}))

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ["username", "password1", "password2"]
```

#### Points importants

- L'authentification de l'utilisateur sur Django est **indépendante** du JWT de Bloc1_data. Django gère ses propres sessions via `django.contrib.sessions`.
- Quand l'app Django appelle les APIs Bloc1 et Bloc3, elle utilise un **compte de service** (username/password stockés en variables d'environnement) pour obtenir un JWT côté serveur. L'utilisateur Django ne voit jamais ce JWT.

### 7.3 App `dashboard`

#### Views

| URL | View | Méthode | Description |
|-----|------|---------|-------------|
| `/dashboard/` | `dashboard_view` | GET | Page principale post-login |
| `/dashboard/charts/` | `charts_view` | GET | Page de visualisation graphiques |
| `/dashboard/api/chart-data/` | `api_chart_data` | GET | API interne JSON pour les graphiques |

#### Dashboard (`dashboard_view`)

Affiche :
- Les **dernières prédictions** pour chaque paire (UP/DOWN/STABLE avec code couleur)
- Un résumé des **statistiques de performance** récentes (accuracy des 7 derniers jours)
- Les prix actuels

#### Graphiques (`charts_view`)

Page avec graphiques interactifs (via Plotly ou Chart.js en JavaScript) :
- **Graphique en chandelier** (candlestick) des données OHLCV
- **Prédictions historiques** superposées en couleur :
  - Vert pour UP
  - Rouge pour DOWN
  - Gris pour STABLE
- Sélecteur de paire et de granularité

#### Service (`dashboard/services.py`)

Fonctions pour appeler Bloc1 data-api :

```python
import requests

class DashboardService:
    def __init__(self):
        self.e1_base_url = settings.API_E1_BASE_URL
        self._token = None

    def _get_token(self):
        """Obtient un JWT depuis Bloc1 avec le compte de service."""
        response = requests.post(
            f"{self.e1_base_url}/api/v1/authentification/login",
            data={"username": settings.E1_SERVICE_USERNAME, "password": settings.E1_SERVICE_PASSWORD}
        )
        self._token = response.json()["access_token"]
        return self._token

    def get_ohlcv(self, trading_pair_id, granularity):
        """Récupère les OHLCV pour une paire."""
        ...

    def get_predictions(self, trading_pair_id, granularity):
        """Récupère les prédictions historiques."""
        ...

    def get_trading_pair(self, base_symbol, quote_symbol):
        """Récupère une paire par symboles."""
        ...
```

### 7.4 App `forecast`

#### Views

| URL | View | Méthode | Description |
|-----|------|---------|-------------|
| `/forecast/` | `classify_view` | GET/POST | Formulaire de classification à la demande |

#### Formulaire

```python
class ClassifyForm(forms.Form):
    PAIR_CHOICES = [("BTC-USDT", "BTC/USDT"), ("BTC-USD", "BTC/USD")]
    GRANULARITY_CHOICES = [("hourly", "Horaire"), ("daily", "Journalier")]
    NUM_PRED_CHOICES = [(i, str(i)) for i in range(1, 25)]

    trading_pair = forms.ChoiceField(choices=PAIR_CHOICES)
    granularity = forms.ChoiceField(choices=GRANULARITY_CHOICES)
    num_pred = forms.ChoiceField(choices=NUM_PRED_CHOICES)
```

#### Résultat affiché

Après soumission, afficher un tableau avec :

| Date | Classe prédite | Confiance |
|------|---------------|-----------|
| 2025-06-15 14:00 | UP | 72.3% |
| 2025-06-15 15:00 | DOWN | 61.8% |
| ... | ... | ... |

Avec un code couleur : vert (UP), rouge (DOWN), gris/orange (STABLE).

#### Service (`forecast/services.py`)

```python
class ForecastService:
    def __init__(self):
        self.e3_base_url = settings.API_E3_BASE_URL
        self._token = None

    def get_classification(self, trading_pair_symbol, granularity, num_pred):
        """Appelle ml-api pour obtenir une classification."""
        token = self._get_token()
        endpoint = "classify_hourly" if granularity == "hourly" else "classify_daily"
        response = requests.post(
            f"{self.e3_base_url}/api/v1/classify/{endpoint}",
            json={"trading_pair_symbol": trading_pair_symbol, "num_pred": num_pred},
            headers={"Authorization": f"Bearer {token}"}
        )
        return response.json()
```

### 7.5 Template de base (`templates/base.html`)

Layout commun HTML avec :
- `<head>` : meta, CSS (framework CSS au choix : Bootstrap ou Tailwind)
- Navbar avec liens : Dashboard, Classification, Graphiques, Déconnexion
- Zone de messages flash (Django `messages` framework)
- Footer
- Bloc `{% block content %}{% endblock %}`

### 7.6 Settings Django (`crypto_app/settings.py`)

Points importants à configurer :

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() in ["true", "1"]

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "accounts",
    "dashboard",
    "forecast",
]

# Base de données PostgreSQL dédiée à Django (ou SQLite en dev)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME", "crypto_webapp"),
        "USER": os.getenv("DJANGO_DB_USER"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD"),
        "HOST": os.getenv("DJANGO_DB_HOST", "localhost"),
        "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
    }
}

# URLs des APIs internes
API_E1_BASE_URL = os.getenv("API_E1_BASE_URL")
API_E3_BASE_URL = os.getenv("API_E3_BASE_URL")
E1_SERVICE_USERNAME = os.getenv("API_E1_SCRIPT_USERNAME")
E1_SERVICE_PASSWORD = os.getenv("API_E1_SCRIPT_PASSWORD")
E3_SERVICE_USERNAME = os.getenv("API_E3_USERNAME")
E3_SERVICE_PASSWORD = os.getenv("API_E3_PASSWORD")

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/"
```

### 7.7 Décorateur d'authentification

Utiliser le décorateur natif Django `@login_required` (de `django.contrib.auth.decorators`) sur toutes les vues protégées.

### 7.8 Dockerfile Django

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["gunicorn", "crypto_app.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]
```

Note : les migrations Django (`python manage.py migrate`) doivent être exécutées avant le démarrage de Gunicorn. Ajouter un `entrypoint.sh` :

```bash
#!/bin/bash
python manage.py migrate --noinput
gunicorn crypto_app.wsgi:application --bind 0.0.0.0:8080 --workers 3
```

---

## 8. Déploiement Docker

### 8.1 docker-compose.yml

```yaml
version: "3.8"

services:
  # === Bloc1 — DATA LAYER ===
  data-scripts:
    build:
      context: ./Bloc1_data
      dockerfile: scripts.Dockerfile
    container_name: data-scripts
    environment:
      - DB_HOST=host.docker.internal
      - DB_PORT=${DB_PORT}
      - DB_NAME=${DB_NAME}
      - DB_USERNAME=${DB_USERNAME}
      - DB_PASSWORD=${DB_PASSWORD}
      - CMC_API_KEY=${CMC_API_KEY}
      - API_E1_SCRIPT_USERNAME=${API_E1_SCRIPT_USERNAME}
      - API_E1_SCRIPT_PASSWORD=${API_E1_SCRIPT_PASSWORD}
      - API_E1_SCRIPT_ROLE=${API_E1_SCRIPT_ROLE}
    extra_hosts:
      - "host.docker.internal:host-gateway"
    volumes:
      - bloc1_logs:/app/data/logs
      - ./Bloc1_data/config:/app/config:ro
    restart: always

  data-api:
    build:
      context: ./Bloc1_data
      dockerfile: api.Dockerfile
    container_name: data-api
    environment:
      - DB_HOST=host.docker.internal
      - DB_PORT=${DB_PORT}
      - DB_NAME=${DB_NAME}
      - DB_USERNAME=${DB_USERNAME}
      - DB_PASSWORD=${DB_PASSWORD}
      - API_E1_SECRET_KEY=${API_E1_SECRET_KEY}
      - API_E1_ALGORITHM=${API_E1_ALGORITHM}
    extra_hosts:
      - "host.docker.internal:host-gateway"
    ports:
      - "8001:8001"
    volumes:
      - ./Bloc1_data/config:/app/config:ro
    restart: always

  # === Bloc3 — ML LAYER ===
  ml-pipeline:
    build:
      context: ./Bloc3_ml
      dockerfile: pipeline.Dockerfile
    container_name: ml-pipeline
    depends_on:
      - data-api
      - mlflow-server
    environment:
      - API_E1_BASE_URL=http://data-api:8001
      - API_E1_SCRIPT_USERNAME=${API_E1_SCRIPT_USERNAME}
      - API_E1_SCRIPT_PASSWORD=${API_E1_SCRIPT_PASSWORD}
      - MLFLOW_TRACKING_URI=http://mlflow-server:5000
      - MODELS_DIR_PATH=/app/models
    volumes:
      - ml_models:/app/models
      - mlruns:/app/mlruns
      - ./Bloc3_ml/config:/app/config:ro
    restart: always

  mlflow-server:
    build:
      context: ./Bloc3_ml
      dockerfile: mlflow.Dockerfile
    container_name: mlflow-server
    ports:
      - "5000:5000"
    volumes:
      - mlruns:/app/mlruns
    restart: always

  ml-api:
    build:
      context: ./Bloc3_ml
      dockerfile: api.Dockerfile
    container_name: ml-api
    environment:
      - API_E3_SECRET_KEY=${API_E3_SECRET_KEY}
      - API_E3_ALGORITHM=${API_E3_ALGORITHM}
      - API_E3_USERNAME=${API_E3_USERNAME}
      - API_E3_PASSWORD=${API_E3_PASSWORD}
      - MODELS_DIR_PATH=/app/models
    ports:
      - "8002:8002"
    volumes:
      - ml_models:/app/models:ro
      - ./Bloc3_ml/config:/app/config:ro
    restart: always

  # === Bloc4 — APPLICATION WEB (Django) ===
  webapp:
    build:
      context: ./Bloc4_app
      dockerfile: app.Dockerfile
    container_name: webapp
    depends_on:
      - data-api
      - ml-api
    environment:
      - API_E1_BASE_URL=http://data-api:8001
      - API_E3_BASE_URL=http://ml-api:8002
      - API_E1_SCRIPT_USERNAME=${API_E1_SCRIPT_USERNAME}
      - API_E1_SCRIPT_PASSWORD=${API_E1_SCRIPT_PASSWORD}
      - API_E3_USERNAME=${API_E3_USERNAME}
      - API_E3_PASSWORD=${API_E3_PASSWORD}
      - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
      - DJANGO_DB_NAME=${DJANGO_DB_NAME}
      - DJANGO_DB_USER=${DJANGO_DB_USER}
      - DJANGO_DB_PASSWORD=${DJANGO_DB_PASSWORD}
      - DJANGO_DB_HOST=host.docker.internal
      - DJANGO_DB_PORT=${DB_PORT}
      - DEBUG=False
    extra_hosts:
      - "host.docker.internal:host-gateway"
    ports:
      - "8080:8080"
    volumes:
      - bloc4_logs:/app/logs
    restart: always

volumes:
  bloc1_logs:
  ml_models:
  mlruns:
  bloc4_logs:
```

### 8.2 Dépendances entre services

```
data-scripts ──(écrit)──▶ PostgreSQL ◀──(lit/écrit)── data-api
                                                          ▲
ml-pipeline ──(dépend de)──▶ data-api                     │
ml-pipeline ──(dépend de)──▶ mlflow-server                │
ml-api ──(lit)──▶ ml_models (volume)                      │
webapp ──(dépend de)──▶ data-api ─────────────────────────┘
webapp ──(dépend de)──▶ ml-api
```

### 8.3 Volumes partagés

| Volume | Utilisé par | Contenu |
|--------|-------------|---------|
| `bloc1_logs` | data-scripts | Logs d'extraction |
| `ml_models` | ml-pipeline (rw), ml-api (ro) | Modèles pickle |
| `mlruns` | ml-pipeline (rw), mlflow-server (rw) | Runs MLflow |
| `bloc4_logs` | webapp | Logs applicatifs |

### 8.4 PostgreSQL

PostgreSQL tourne sur la machine hôte (pas dans Docker). Les conteneurs y accèdent via `host.docker.internal:host-gateway`.

Il y a 2 bases :
- `crypto_db` : utilisée par Bloc1 (data-api, data-scripts) et Bloc3 (ml-pipeline)
- `crypto_webapp` : utilisée par Bloc4 (Django, pour les sessions et users Django)

### 8.5 Ordre de démarrage

1. PostgreSQL (sur l'hôte) doit être démarré en premier
2. `docker-compose up -d` lance tout le reste
3. `data-scripts` initialise la BDD au premier lancement (fichier de verrouillage)
4. `data-api` devient disponible sur :8001
5. `mlflow-server` devient disponible sur :5000
6. `ml-pipeline` attend `data-api` et `mlflow-server`
7. `ml-api` charge les modèles depuis le volume
8. `webapp` attend `data-api` et `ml-api`

---

## 9. Variables d'environnement

### .env.example

```env
# === PostgreSQL (Bloc1/Bloc3) ===
DB_HOST=localhost
DB_PORT=5432
DB_NAME=crypto_db
DB_USERNAME=postgres
DB_PASSWORD=changeme

# === CoinMarketCap ===
CMC_API_KEY=votre_cle_cmc

# === API Bloc1 (data-api) ===
API_E1_SECRET_KEY=votre_secret_e1
API_E1_ALGORITHM=HS256

# === Compte de service Bloc1 (utilisé par data-scripts et ml-pipeline) ===
API_E1_SCRIPT_USERNAME=script_user
API_E1_SCRIPT_PASSWORD=script_password
API_E1_SCRIPT_ROLE=script

# === API Bloc3 (ml-api) ===
API_E3_SECRET_KEY=votre_secret_e3
API_E3_ALGORITHM=HS256
API_E3_USERNAME=ml_user
API_E3_PASSWORD=ml_password

# === MLflow ===
MLFLOW_TRACKING_URI=http://localhost:5000

# === Django (Bloc4) ===
DJANGO_SECRET_KEY=votre_secret_django
DJANGO_DB_NAME=crypto_webapp
DJANGO_DB_USER=postgres
DJANGO_DB_PASSWORD=changeme

# === Token Metrics (Bloc2 - veille) ===
TOKEN_METRICS_API_KEY=votre_cle_token_metrics
```

---

## 10. Tests

### 10.1 Structure des tests

Chaque couche a son dossier `tests/` avec :

| Type | Outil | Couverture cible |
|------|-------|-----------------|
| Tests unitaires | pytest | Fonctions de feature engineering, calcul de la cible, métriques |
| Tests d'intégration | pytest + httpx (FastAPI TestClient) | Endpoints API Bloc1 et Bloc3 |
| Tests Django | pytest-django ou `django.test.TestCase` | Views, formulaires, services |

### 10.2 Exemples de tests critiques

#### Bloc1 — Data

- `test_fetch_binance_data` : vérifie que le DataFrame retourné a les bonnes colonnes
- `test_save_ohlcv_to_db` : vérifie l'insertion en BDD
- `test_api_login` : vérifie la génération de JWT
- `test_api_ohlcv_endpoint` : vérifie la réponse de l'endpoint OHLCV

#### Bloc3 — ML

- `test_build_features` : vérifie que les indicateurs techniques sont calculés correctement
- `test_target_construction` : vérifie la construction de la variable cible avec différents seuils
- `test_model_training` : vérifie qu'un modèle peut être entraîné sans erreur
- `test_model_prediction` : vérifie que les prédictions sont dans {0, 1, 2}
- `test_api_classify` : vérifie l'endpoint de classification

#### Bloc4 — Django

- `test_login_view` : vérifie le formulaire de connexion
- `test_dashboard_requires_login` : vérifie la redirection si non authentifié
- `test_forecast_service` : vérifie l'appel à ml-api

### 10.3 Lancement

```bash
# Depuis la racine du projet
pytest --cov=Bloc1_data --cov=Bloc3_ml --cov=Bloc4_app --cov-report=html
```

---

## 11. Annexes techniques

### 11.1 Différences clés avec un projet de régression (prédiction de prix)

| Aspect | Régression (prix) | Classification (tendance) |
|--------|-------------------|--------------------------|
| Variable cible | Prix (float continu) | Classe (0, 1, 2) |
| Modèles | XGBRegressor, Darts TimeSeries | XGBClassifier, RandomForest, LogisticRegression |
| Features | Principalement lags du prix close | Lags + indicateurs techniques (RSI, MACD, BB...) |
| Métriques | MAPE, MAE | Accuracy, F1-score, matrice de confusion |
| Sortie API | Liste de prix prédits | Classe + label + confiance |
| Affichage | Courbe de prix prédits | Couleurs (vert/rouge/gris) sur les bougies |

### 11.2 Gestion du déséquilibre des classes

La distribution UP/DOWN/STABLE peut être déséquilibrée. Stratégies :
- Utiliser `class_weight="balanced"` dans les modèles qui le supportent
- Ajuster le seuil de classification (paramètre `seuil` dans `ml_config.yaml`)
- Monitorer la distribution via MLflow (log le support par classe)

### 11.3 Librairie d'indicateurs techniques

Recommandation : utiliser `pandas-ta`.

Installation : `pip install pandas-ta`

Exemple d'utilisation :

```python
import pandas_ta as ta

df["rsi"] = ta.rsi(df["close"], length=14)
macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
df = pd.concat([df, macd], axis=1)
bbands = ta.bbands(df["close"], length=20, std=2)
df = pd.concat([df, bbands], axis=1)
df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)
df["sma_7"] = ta.sma(df["close"], length=7)
df["ema_12"] = ta.ema(df["close"], length=12)
```

### 11.4 Sauvegarde et chargement des modèles

```python
import joblib

# Sauvegarde
joblib.dump(model, f"{models_dir}/{granularity}_models/{symbol}.pkl")

# Chargement
model = joblib.load(f"{models_dir}/{granularity}_models/{symbol}.pkl")
```

### 11.5 Format de réponse de l'API de classification

```json
{
  "trading_pair_symbol": "BTC-USDT",
  "num_pred": 3,
  "predictions": [
    {
      "date": "2025-06-15T14:00:00",
      "predicted_class": 2,
      "predicted_label": "UP",
      "confidence": 0.723
    },
    {
      "date": "2025-06-15T15:00:00",
      "predicted_class": 0,
      "predicted_label": "DOWN",
      "confidence": 0.618
    },
    {
      "date": "2025-06-15T16:00:00",
      "predicted_class": 1,
      "predicted_label": "STABLE",
      "confidence": 0.542
    }
  ]
}
```

### 11.6 Checklist de construction du projet

1. [ ] Créer le repo Git et l'arborescence
2. [ ] Configurer PostgreSQL sur l'hôte (créer les 2 bases)
3. [ ] Implémenter Bloc1 : extraction CoinMarketCap
4. [ ] Implémenter Bloc1 : extraction CryptoDownload
5. [ ] Implémenter Bloc1 : modèles SQLAlchemy et initialisation BDD
6. [ ] Implémenter Bloc1 : extraction Binance (update incrémental)
7. [ ] Implémenter Bloc1 : API FastAPI (auth, ohlcv, trading_pairs, predictions)
8. [ ] Implémenter Bloc1 : Dockerfiles + entrypoint.sh + cron
9. [ ] Implémenter Bloc2 : script Token Metrics + documentation
10. [ ] Implémenter Bloc3 : fetch_data (depuis Bloc1 API)
11. [ ] Implémenter Bloc3 : build_features (indicateurs techniques + cible)
12. [ ] Implémenter Bloc3 : train_model + predict_model
13. [ ] Implémenter Bloc3 : evaluate_model (métriques de classification)
14. [ ] Implémenter Bloc3 : monitor_training (MLflow)
15. [ ] Implémenter Bloc3 : pipeline principal + save_model
16. [ ] Implémenter Bloc3 : send_data (POST predictions vers Bloc1)
17. [ ] Implémenter Bloc3 : API FastAPI (classify endpoints)
18. [ ] Implémenter Bloc3 : Dockerfiles + entrypoint.sh + cron
19. [ ] Implémenter Bloc4 : projet Django + settings
20. [ ] Implémenter Bloc4 : app accounts (login, register)
21. [ ] Implémenter Bloc4 : app dashboard (OHLCV + prédictions)
22. [ ] Implémenter Bloc4 : app forecast (classification à la demande)
23. [ ] Implémenter Bloc4 : templates (base, pages, graphiques)
24. [ ] Implémenter Bloc4 : Dockerfile + entrypoint.sh
25. [ ] Rédiger le docker-compose.yml
26. [ ] Configurer le .env
27. [ ] Écrire les tests (Bloc1, Bloc3, Bloc4)
28. [ ] Rédiger le README.md
29. [ ] Tester le déploiement complet avec `docker-compose up`
