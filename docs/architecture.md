# Architecture Technique — Plateforme Crypto Certification

## 1. Vue d'ensemble

La plateforme est composée de 4 blocs fonctionnels, orchestrés via Docker Compose :

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        UTILISATEUR (Navigateur)                             │
│                              │                                              │
│                              ▼ :8090                                        │
│  ┌─────────────────────────────────────────────┐                           │
│  │         BLOC 4 — Django (webapp)            │                           │
│  │  Dashboard | Charts | Forecast | Accounts   │                           │
│  └──────────────┬──────────────┬───────────────┘                           │
│                 │              │                                             │
│         JWT     │              │  JWT                                        │
│                 ▼ :8001        ▼ :8002                                      │
│  ┌──────────────────┐   ┌──────────────────┐                              │
│  │  BLOC 1 — API    │   │  BLOC 3 — API ML │                              │
│  │  FastAPI (data)   │   │  FastAPI (classify)│                             │
│  │  /ohlcv, /pairs   │   │  /classify_daily  │                              │
│  └────────┬─────────┘   └────────┬──────────┘                              │
│           │                       │                                          │
│           ▼                       ▼                                          │
│  ┌──────────────┐       ┌──────────────────┐                               │
│  │ PostgreSQL   │       │  Modèles .pkl    │                               │
│  │ (crypto_db)  │       │  (Volume Docker) │                               │
│  └──────────────┘       └──────────────────┘                               │
│                                                                              │
│  ┌──────────────────────────────────────────┐                               │
│  │          MONITORING                       │                               │
│  │  Prometheus (:9090) + Grafana (:3000)    │                               │
│  └──────────────────────────────────────────┘                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. Services Docker Compose

| Service | Image/Build | Port exposé | Rôle |
|---------|-------------|-------------|------|
| `db` | postgres:16 | — | Base de données principale |
| `data-scripts` | Bloc1_data/scripts.Dockerfile | — | Init DB + cron extraction |
| `data-api` | Bloc1_data/api.Dockerfile | 8003→8001 | API REST données |
| `ml-pipeline` | Bloc3_ml/pipeline.Dockerfile | — | Cron entraînement + prédictions |
| `mlflow-server` | Bloc3_ml/mlflow.Dockerfile | 5000 | UI monitoring ML |
| `ml-api` | Bloc3_ml/api.Dockerfile | 8002 | API classification |
| `webapp` | Bloc4_app/app.Dockerfile | 8090→8080 | Application Django |
| `prometheus` | prom/prometheus | 9090 | Collecte métriques |
| `grafana` | grafana/grafana | 3000 | Visualisation métriques |

## 3. Flux de données

### 3.1 Collecte (Bloc1)
```
Binance API ──REST──> data-scripts ──SQLAlchemy──> PostgreSQL
CoinMarketCap ──REST──> data-scripts ──SQLAlchemy──> PostgreSQL
CSV historiques ──parse──> data-scripts ──SQLAlchemy──> PostgreSQL
```

### 3.2 Entraînement ML (Bloc3)
```
data-api ──JWT/REST──> ml-pipeline ──pandas-ta──> features
features ──XGBoost──> modèle .pkl
modèle ──évaluation──> MLflow (métriques)
modèle ──prédiction──> data-api (POST /predictions)
```

### 3.3 Application (Bloc4)
```
Utilisateur ──HTTP──> Django ──JWT──> data-api (OHLCV, prédictions)
Utilisateur ──HTTP──> Django ──JWT──> ml-api (classification à la demande)
```

### 3.4 Monitoring
```
data-api ──/metrics──> Prometheus ──scrape 15s──> Grafana
ml-api ──/metrics──> Prometheus ──scrape 15s──> Grafana
```

## 4. Technologies

| Couche | Technologie | Justification |
|--------|-------------|---------------|
| Base de données | PostgreSQL 16 | Robuste, performant pour les séries temporelles |
| API | FastAPI | Performance async, documentation OpenAPI auto |
| ML | XGBoost, scikit-learn | État de l'art pour la classification tabulaire |
| Monitoring ML | MLflow | Standard open-source, tracking métriques + artefacts |
| Application | Django 5 | Framework complet (auth, ORM, templates, admin) |
| Frontend | Bootstrap 5 | Responsive, rapide à mettre en place |
| Conteneurisation | Docker Compose | Reproductibilité, isolation des services |
| CI | GitHub Actions | Intégré au workflow Git, gratuit pour projets publics |
| Monitoring | Prometheus + Grafana | Standard cloud-native, dashboards riches |
| Gestion dépendances | uv | Rapide, lockfile déterministe |

## 5. Sécurité

| Mécanisme | Implémentation |
|-----------|---------------|
| Authentification API | JWT (python-jose) avec secret en variable d'env |
| Authentification webapp | Sessions Django + cookies sécurisés |
| Protection CSRF | Middleware Django |
| Hashage passwords | bcrypt (Bloc1), PBKDF2 (Django) |
| Isolation réseau | Docker network interne (services non exposés sauf ports nécessaires) |
| Validation entrées | Pydantic (FastAPI), Django Forms |

## 6. Démarrage rapide

```bash
# 1. Copier la configuration
cp .env.example .env
# Éditer .env avec vos clés API

# 2. Lancer tous les services
docker compose up -d

# 3. Accéder aux interfaces
# Application web : http://localhost:8090
# API données :    http://localhost:8003/docs
# API ML :         http://localhost:8002/docs
# MLflow :         http://localhost:5000
# Grafana :        http://localhost:3000 (admin/admin)
# Prometheus :     http://localhost:9090
```
