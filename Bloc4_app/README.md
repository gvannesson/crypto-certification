# Bloc4 — Application Web (Django)

Application web de consultation des données crypto et des prédictions de tendance.

## Architecture

```
Bloc4_app/
├── accounts/             # Module authentification (login, register, logout)
├── dashboard/            # Module dashboard (vue d'ensemble + graphiques)
├── forecast/             # Module prédiction (classification à la demande)
├── crypto_app/           # Configuration Django (settings, urls, wsgi)
├── templates/            # Template de base (navbar, footer)
├── static/css/           # Styles CSS personnalisés
├── tests/                # Tests pytest (accounts, dashboard, forecast, services)
├── app.Dockerfile        # Image Docker
├── entrypoint.sh         # Démarrage (migrate + collectstatic + gunicorn)
└── manage.py             # CLI Django
```

## Installation

### Prérequis
- Python 3.11+
- PostgreSQL (pour la production) ou SQLite (pour les tests)

### En local
```bash
cd Bloc4_app
uv sync --dev
uv run python manage.py migrate
uv run python manage.py runserver
```

### Via Docker
```bash
docker compose up webapp -d
# Accessible sur http://localhost:8090
```

## Fonctionnalités

### Accounts (authentification)
- Inscription avec formulaire (username + mot de passe)
- Connexion / déconnexion
- Protection des vues via `@login_required`
- Protection CSRF (middleware Django)

### Dashboard
- Vue d'ensemble : dernier prix et dernière prédiction par paire
- Graphiques interactifs (OHLCV + prédictions) chargés en AJAX
- Sélection de la paire et de la granularité

### Forecast (classification)
- Formulaire : paire, granularité (daily/hourly), nombre de prédictions (1-7 ou 1-24)
- Appel à l'API ML (Bloc3) en temps réel
- Affichage des résultats (date, classe, label, confiance)
- Gestion des erreurs (API indisponible)

## Communication inter-services

```
Webapp (Django) ──JWT──> data-api (Bloc1)   [OHLCV, trading_pairs, predictions]
Webapp (Django) ──JWT──> ml-api (Bloc3)     [classify_daily, classify_hourly]
```

L'authentification inter-services est gérée par `services.py` dans chaque module, qui :
1. Obtient un token JWT via `/login`
2. Utilise le token pour les requêtes suivantes
3. Gère le renouvellement en cas d'expiration

## Intégration Continue (C18)

### GitHub Actions (`.github/workflows/ci.yml`)

**Déclencheurs :** push et PR sur `main` / `develop`

**Étapes :**
1. Checkout du code
2. Installation de `uv` et Python 3.11
3. Installation des dépendances (`uv sync --dev`)
4. Exécution des tests (`pytest` avec couverture)
5. Upload du rapport de couverture

**Variables d'environnement CI :**
- Base de données SQLite en mémoire (pas besoin de PostgreSQL)
- URLs des APIs simulées (les tests mockent les appels HTTP)

### Exécution locale des tests
```bash
cd Bloc4_app
uv run pytest tests/ -v --cov=accounts --cov=dashboard --cov=forecast --cov-report=term-missing
```

### Couverture de tests
- `test_accounts.py` — Inscription, connexion, déconnexion, accès protégé
- `test_dashboard.py` — Vues dashboard et charts
- `test_forecast.py` — Formulaire et appel classification
- `test_services.py` — Communication avec les APIs Bloc1/Bloc3

## Livraison Continue (C19)

### Processus de build
1. Chaque bloc a son propre `Dockerfile` (build multi-stage avec `uv`)
2. `docker-compose.yml` orchestre l'ensemble des services
3. Les images sont construites automatiquement au `docker compose up --build`

### Processus de déploiement
1. Développement sur branche feature (`bloc1_data`, `bloc2_veille`, etc.)
2. PR vers `main` → CI lance les tests
3. Merge après review → build des images Docker
4. Déploiement via `docker compose up -d`

## Sécurité (OWASP)

| Risque OWASP | Mitigation |
|-------------|-----------|
| A01 Broken Access Control | `@login_required` sur toutes les vues |
| A02 Cryptographic Failures | Passwords hashés (PBKDF2), JWT secret en variable d'env |
| A03 Injection | ORM Django (pas de SQL brut), validation formulaires |
| A05 Security Misconfiguration | `DEBUG=False` en production, `SECRET_KEY` en env |
| A08 CSRF | Middleware CSRF Django activé |
