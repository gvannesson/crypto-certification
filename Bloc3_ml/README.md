# Bloc3 — Machine Learning Pipeline

Entraînement, évaluation et déploiement de modèles de classification de tendance crypto (UP / STABLE / DOWN).

## Architecture

```
Bloc3_ml/
├── src/
│   ├── api/              # API FastAPI de classification à la demande
│   │   ├── routes/       # Endpoints (classify, login)
│   │   └── utils/        # Auth, classes, fonctions utilitaires
│   ├── data/             # Récupération des données depuis l'API Bloc1
│   ├── features/         # Construction des features (indicateurs techniques)
│   ├── model/            # Entraînement, évaluation, sauvegarde, prédiction
│   ├── monitoring/       # Logging des métriques vers MLflow
│   └── utils/            # Classes et fonctions partagées
├── config/               # Configuration YAML (données, modèles, ML)
├── tests/                # Tests pytest
├── api.Dockerfile        # Image Docker de l'API ML
├── pipeline.Dockerfile   # Image Docker du pipeline (cron)
├── mlflow.Dockerfile     # Image Docker du serveur MLflow
└── entrypoint.sh         # Démarrage du pipeline (cron)
```

## Installation

```bash
cd Bloc3_ml
uv sync --dev
```

## Modèles

### Configuration

| Paramètre | Valeur |
|-----------|--------|
| Algorithme principal | XGBoost (XGBClassifier) |
| Alternatives testées | Random Forest, Logistic Regression |
| Classes | 0 = DOWN, 1 = STABLE, 2 = UP |
| Seuil de classification | 0.5% de variation |
| Features | Indicateurs techniques (RSI, MACD, Bollinger, SMA, EMA, etc.) |

### Modèles entraînés

| Paire | Granularité | Période d'entraînement | Période de test |
|-------|-------------|----------------------|-----------------|
| BTCUSDT | Daily | 2020-01-01 → 2024-12-31 | 2025-01-01 → 2025-05-31 |
| BTCUSDT | Hourly | 2024-01-01 → 2024-12-31 | 2025-01-01 → 2025-03-31 |

## MLflow — Monitoring des modèles (C8, C11)

**Interface :** http://localhost:5000

### Métriques trackées
| Métrique | Description |
|----------|-------------|
| `accuracy` | Taux de classification correcte |
| `f1_macro` | F1-score macro (équilibré entre classes) |
| `direction_accuracy` | Précision de la direction (hausse/baisse) |

### Accès
```bash
docker compose up mlflow-server -d
# Interface disponible sur http://localhost:5000
```

## API de Classification (C9)

**Port :** 8002  
**Documentation :** http://localhost:8002/docs

### Endpoints

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/v1/login` | Obtenir un token JWT | Non |
| POST | `/api/v1/classify/classify_daily` | Classification journalière (1-7 prédictions) | JWT |
| POST | `/api/v1/classify/classify_hourly` | Classification horaire (1-24 prédictions) | JWT |
| GET | `/metrics` | Métriques Prometheus | Non |
| GET | `/health` | Healthcheck | Non |

### Exemple d'appel
```bash
# Login
TOKEN=$(curl -s -X POST http://localhost:8002/api/v1/login \
  -H "Content-Type: application/json" \
  -d '{"username":"ml_user","password":"ml_password"}' | jq -r '.access_token')

# Classification
curl -X POST http://localhost:8002/api/v1/classify/classify_daily \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"trading_pair_symbol":"BTCUSDT","num_pred":3}'
```

## Chaîne MLOps (C13)

### Pipeline de re-entraînement

```
┌────────────┐    ┌──────────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Fetch Data │ -> │Build Features│ -> │  Train   │ -> │ Evaluate │ -> │  Save    │
│  (API E1)  │    │ (pandas-ta)  │    │(XGBoost) │    │(MLflow)  │    │(.pkl)    │
└────────────┘    └──────────────┘    └──────────┘    └──────────┘    └──────────┘
```

### Déclencheurs (Cron)
| Fréquence | Commande | Description |
|-----------|----------|-------------|
| Toutes les heures (XX:05) | `update_models_and_predictions.py --granularity hour` | Re-entraînement horaire |
| Quotidien (00:03) | `update_models_and_predictions.py --granularity day` | Re-entraînement journalier |

### Artefacts produits
- Modèles sérialisés (`.pkl`) dans le volume Docker `ml_models`
- Métriques loguées dans MLflow (volume `mlruns`)
- Prédictions envoyées vers l'API Bloc1 (POST /predictions)

## Tests

```bash
cd Bloc3_ml
uv run pytest tests/ -v --cov=src --cov-report=term-missing
```

### Couverture
- `test_build_features.py` — Validation des features calculées
- `test_evaluate_model.py` — Validation des métriques
- `test_api_classify.py` — Tests des endpoints de classification
- `test_api_auth.py` — Tests de l'authentification
