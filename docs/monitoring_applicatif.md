# Monitoring Applicatif — Prometheus + Grafana

## 1. Architecture

```
+-------------+       +-------------+       +-----------+
|  data-api   |------>|             |       |           |
|  /metrics   |       | Prometheus  |------>|  Grafana  |
+-------------+       |  (scrape    |       | (dashboard|
                      |   15s)      |       |  + alertes|
+-------------+       |             |       |           |
|   ml-api    |------>|             |       |           |
|  /metrics   |       +-------------+       +-----------+
+-------------+         port 9090            port 3000
```

## 2. Métriques collectées

Chaque API FastAPI expose automatiquement (via `prometheus-fastapi-instrumentator`) :

| Métrique | Type | Description |
|----------|------|-------------|
| `http_requests_total` | Counter | Nombre total de requêtes par endpoint, méthode, status |
| `http_request_duration_seconds` | Histogram | Latence par requête (buckets : 0.01 à 10s) |
| `http_requests_in_progress` | Gauge | Requêtes en cours de traitement |
| `http_request_size_bytes` | Summary | Taille des requêtes entrantes |
| `http_response_size_bytes` | Summary | Taille des réponses sortantes |

## 3. Seuils d'alerte

| Alerte | Condition | Sévérité | Durée avant déclenchement |
|--------|-----------|----------|---------------------------|
| HighErrorRate | > 5% de requêtes en 5xx sur 5min | Warning | 2 minutes |
| HighLatency | p95 > 5 secondes sur 5min | Warning | 3 minutes |
| ServiceDown | Service ne répond plus | Critical | 1 minute |

Ces règles sont évaluées par Prometheus (visibles sur http://localhost:9090/alerts, état
`inactive`/`pending`/`firing`) mais **aucun Alertmanager n'est déployé** : une alerte qui passe
`firing` reste visible dans l'UI Prometheus, sans notification externe (Slack, e-mail...) —
limite assumée pour ce projet local, cf. rapport E5.

## 4. Installation et configuration

### Prérequis
- Docker et Docker Compose installés
- Aucune dépendance supplémentaire (images Docker officielles)

### Démarrage
```bash
docker compose up -d prometheus grafana
```

### Accès aux interfaces
| Service | URL | Identifiants |
|---------|-----|-------------|
| Prometheus | http://localhost:9090 | — |
| Grafana | http://localhost:3000 | admin / admin |
| Métriques data-api | http://localhost:8003/metrics | — |
| Métriques ml-api | http://localhost:8002/metrics | — |

### Vérification
```bash
# Vérifier que Prometheus scrape les targets
curl http://localhost:9090/api/v1/targets | jq '.data.activeTargets[] | {job: .labels.job, health: .health}'

# Vérifier que les métriques sont exposées
curl http://localhost:8003/metrics | head -20
```

## 5. Dashboard Grafana

Le dashboard pré-provisionné ("API Monitoring - Crypto Certification") affiche :

1. **Requêtes par seconde** — vue temps réel du trafic
2. **Taux d'erreur 5xx** — par service (data-api, ml-api)
3. **Latence p50/p95/p99** — distribution des temps de réponse
4. **Status UP/DOWN** — vue instantanée de la disponibilité
5. **Requêtes par endpoint** — tableau détaillé par API

## 6. Choix techniques et justification

| Choix | Justification |
|-------|--------------|
| Prometheus | Standard de facto pour le monitoring cloud-native, modèle pull, PromQL puissant |
| Grafana | Visualisation riche, provisionning as code, écosystème de dashboards |
| prometheus-fastapi-instrumentator | Intégration zéro-config avec FastAPI, métriques standards |
| Scrape interval 15s | Bon compromis granularité/charge pour un projet de cette taille |

## 7. Éco-responsabilité

- Rétention Prometheus configurée à 15 jours par défaut (pas de stockage infini)
- Images Docker légères (< 100MB chacune)
- Scraping passif : Prometheus interroge les APIs, pas de push continu
- Les métriques n'impactent pas les performances des APIs (< 1ms overhead)
