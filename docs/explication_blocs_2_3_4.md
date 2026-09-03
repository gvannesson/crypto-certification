# Explication des Blocs 2, 3 et 4

## Vue d'ensemble

Le projet est une plateforme de **classification de tendance** pour les cryptomonnaies (BTC-USD et BTC-USDT). Il prédit si le prix va **monter (UP)**, **descendre (DOWN)** ou **rester stable (STABLE)** à chaque pas de temps.

Le projet est découpé en 4 blocs indépendants qui communiquent via des APIs REST :

| Bloc | Rôle | Technologie | Port |
|------|------|-------------|------|
| Bloc1_data | Extraction et stockage des données OHLCV | FastAPI + PostgreSQL | 8001 |
| Bloc2_veille | Veille technologique (Token Metrics) | Script Python standalone | — |
| Bloc3_ml | Entraînement et prédiction ML | FastAPI + scikit-learn + MLflow | 8002 / 5000 |
| Bloc4_app | Application web utilisateur | Django | 8080 |

---

## Bloc2 — Veille technologique

**Fichier principal :** `Bloc2_veille/parametrage.py`

Script autonome (non dockerisé) qui interroge l'API Token Metrics pour récupérer des signaux de trading. Il sert à montrer la capacité de veille sur des sources de données externes.

### Fonctionnement

1. Charge la clé API depuis `.env`
2. Appelle `/v2/trading-signals`
3. Construit un DataFrame avec les colonnes : TOKEN_NAME, TOKEN_SYMBOL, DATE, TRADING_SIGNAL, TOKEN_TREND, etc.
4. Affiche les résultats

### Lancer

```bash
cd Bloc2_veille
pip install -r requirements.txt
python parametrage.py
```

---

## Bloc3 — Couche Machine Learning

### Architecture interne

```
Bloc3_ml/
├── update_models_and_predictions.py   # Pipeline principal (exécuté par cron)
├── entrypoint.sh                      # Cron pour lancer le pipeline
├── config/                            # Fichiers YAML de configuration
└── src/
    ├── settings.py                    # Chargement config + variables d'env
    ├── utils/classes.py               # TradingPairClassifier
    ├── data/                          # Communication avec Bloc1 API
    │   ├── fetch_data.py              # GET OHLCV
    │   └── send_data.py              # POST prédictions
    ├── features/build_features.py     # Feature engineering
    ├── model/                         # Logique ML
    │   ├── initiate_classifier.py     # Init classifiers + fetch OHLCV + features
    │   ├── train_model.py             # Entraîne le modèle
    │   ├── predict_model.py           # Prédit UP/DOWN/STABLE
    │   ├── evaluate_model.py          # Calcule accuracy, F1, etc.
    │   └── save_model.py             # Sauvegarde en pickle
    ├── monitoring/monitor_training.py # Log dans MLflow
    └── api/                          # FastAPI pour classification à la demande
```

### Pipeline ML (`update_models_and_predictions.py`)

Exécuté toutes les heures et tous les jours par cron. Les étapes sont :

1. **Initialisation** : crée un `TradingPairClassifier` par paire, récupère les OHLCV depuis Bloc1 via JWT, calcule les features
2. **Évaluation** : entraîne/évalue sur des fenêtres glissantes, log les métriques dans MLflow
3. **Prédiction** : entraîne sur toutes les données, prédit la prochaine bougie
4. **Envoi** : POST les prédictions vers Bloc1 API
5. **Sauvegarde** : dump le modèle en fichier pickle

### Feature Engineering

Les features construites à partir des OHLCV bruts :

- **Lags autorégressifs** : close, volume, high, low (24 lags horaire / 7 lags journalier)
- **Rendements** : pct_change sur 1, 3, 6, 12 périodes
- **Indicateurs techniques** (via pandas-ta) : RSI, MACD, Bollinger Bands, SMA, EMA, ATR
- **Features temporelles** : heure, jour de la semaine, mois, is_weekend
- **Variable cible** : variation du close classifiée en DOWN (0), STABLE (1), UP (2) avec un seuil de 0.5%

### Modèles

Trois modèles sont configurables par YAML :
- **XGBClassifier** (par défaut) — bon sur données tabulaires
- **RandomForestClassifier** — benchmark d'ensemble
- **LogisticRegression** — baseline simple

Le modèle utilisé par paire se configure dans `hour_models_config.yaml` / `day_models_config.yaml`.

### Métriques

- Accuracy, F1 macro, F1 par classe (UP, DOWN, STABLE)
- Direction accuracy (% de bonnes prédictions UP vs DOWN)
- Tout est loggé dans MLflow (accessible sur le port 5000)

### API ML (port 8002)

- `POST /api/v1/authentification/login` — obtenir un JWT
- `POST /api/v1/classify/classify_hourly` — classification horaire à la demande
- `POST /api/v1/classify/classify_daily` — classification journalière à la demande

Le corps de requête attend `trading_pair_symbol` et `num_pred`. La réponse contient la classe prédite, le label et la confiance.

---

## Bloc4 — Application Web Django

### Architecture interne

```
Bloc4_app/
├── manage.py
├── crypto_app/            # Projet Django (settings, urls, wsgi)
├── accounts/              # App : authentification
├── dashboard/             # App : dashboard + graphiques
├── forecast/              # App : classification à la demande
├── templates/base.html    # Layout commun (Bootstrap 5)
└── static/css/style.css
```

### App `accounts`

Authentification via le système natif de Django (`django.contrib.auth`). Trois vues :
- **Login** (`/login/`) : formulaire de connexion
- **Register** (`/register/`) : formulaire d'inscription
- **Logout** (`/logout/`) : déconnexion

L'auth Django est indépendante du JWT Bloc1/Bloc3. Les appels aux APIs internes utilisent un **compte de service** (identifiants dans les variables d'environnement).

### App `dashboard`

- **Dashboard** (`/dashboard/`) : affiche les dernières prédictions par paire avec code couleur (vert=UP, rouge=DOWN, gris=STABLE) et le prix courant
- **Graphiques** (`/dashboard/charts/`) : graphique chandelier OHLCV interactif (Plotly.js) avec sélecteur de paire et granularité
- **API JSON** (`/dashboard/api/chart-data/`) : endpoint interne AJAX pour les données graphiques

Le service `DashboardService` gère l'authentification JWT vers Bloc1 et expose les méthodes pour récupérer OHLCV, prédictions et trading pairs.

### App `forecast`

- **Classification** (`/forecast/`) : formulaire avec choix de la paire, granularité et nombre de prédictions
- Soumet la requête à `ml-api` (Bloc3) et affiche un tableau de résultats coloré

### Templates

Le layout utilise **Bootstrap 5** (CDN). La navbar affiche les liens Dashboard, Graphiques, Classification et Déconnexion.

---

## Docker Compose

Tous les services (sauf PostgreSQL qui tourne sur l'hôte) sont orchestrés par `docker-compose.yml` :

| Service | Image | Port | Rôle |
|---------|-------|------|------|
| data-scripts | Bloc1_data/scripts.Dockerfile | — | Cron extraction OHLCV |
| data-api | Bloc1_data/api.Dockerfile | 8001 | API données |
| ml-pipeline | Bloc3_ml/pipeline.Dockerfile | — | Cron ML |
| mlflow-server | Bloc3_ml/mlflow.Dockerfile | 5000 | UI MLflow |
| ml-api | Bloc3_ml/api.Dockerfile | 8002 | API classification |
| webapp | Bloc4_app/app.Dockerfile | 8080 | App Django |

### Volumes partagés

- `ml_models` : modèles pickle (partagé entre ml-pipeline et ml-api)
- `mlruns` : données MLflow

### Démarrage

```bash
# 1. Copier et remplir le .env
cp .env.example .env

# 2. PostgreSQL doit tourner sur l'hôte avec les bases crypto_db et crypto_webapp

# 3. Lancer tout
docker-compose up -d
```
