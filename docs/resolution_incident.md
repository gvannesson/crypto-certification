# Résolution d'incident — Erreur 500 sur l'endpoint OHLCV avec paramètre `start_date` invalide

## 1. Contexte

**Date de découverte :** Sprint 4 — Phase d'intégration Bloc4 → Bloc1  
**Sévérité :** Moyenne  
**Service affecté :** data-api (Bloc1, FastAPI)  
**Endpoint :** `GET /ohlcv/daily_by_trading_pair_id?trading_pair_id=1&start_date=invalid`

---

## 2. Description du problème

Lors de l'intégration de l'application Django (Bloc4) avec l'API data (Bloc1), une erreur 500 non gérée se produit lorsque le paramètre `start_date` contient une valeur invalide (ex: chaîne non-date, format inattendu).

**Comportement observé :**
```
HTTP 500 Internal Server Error
{
  "detail": "Internal Server Error"
}
```

**Comportement attendu :**
```
HTTP 422 Unprocessable Entity
{
  "detail": "Format de date invalide. Utiliser YYYY-MM-DD"
}
```

---

## 3. Étapes de reproduction

### Environnement
- Docker compose (services : db, data-api)
- PostgreSQL 16, FastAPI

### Reproduction
```bash
# 1. Démarrer les services
docker compose up db data-api -d

# 2. Obtenir un token JWT
TOKEN=$(curl -s -X POST http://localhost:8003/login \
  -H "Content-Type: application/json" \
  -d '{"username":"script_user","password":"script_password"}' | jq -r '.access_token')

# 3. Appel avec une date invalide → 500
curl -s http://localhost:8003/ohlcv/daily_by_trading_pair_id?trading_pair_id=1&start_date=not-a-date \
  -H "Authorization: Bearer $TOKEN"
# Résultat : 500 Internal Server Error

# 4. Appel avec une date valide → 200 (confirmation que c'est le paramètre)
curl -s http://localhost:8003/ohlcv/daily_by_trading_pair_id?trading_pair_id=1&start_date=2025-01-01 \
  -H "Authorization: Bearer $TOKEN"
# Résultat : 200 OK avec données
```

---

## 4. Analyse de la cause racine

### Investigation
Le fichier `Bloc1_data/src/C5_api/routes/ohlcv.py` montre que le paramètre `start_date` est déclaré comme `str = None` sans aucune validation :

```python
@router.get("/daily_by_trading_pair_id")
def get_ohlcv_daily(trading_pair_id: int, start_date: str = None, ...):
    return db.ohlcv_daily.get_ohlcv_by_trading_pair(trading_pair_id, start_date)
```

La valeur est passée directement à la couche base de données, qui tente de l'utiliser dans une clause SQL `WHERE date >= 'not-a-date'`, provoquant une exception PostgreSQL non interceptée.

### Cause racine
Absence de validation du format de date en entrée de l'endpoint. Pas de gestion d'erreur entre la couche API et la couche BDD.

---

## 5. Solution implémentée

### Fichier modifié : `Bloc1_data/src/C5_api/routes/ohlcv.py`

```python
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from src.C5_api.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/ohlcv", tags=["ohlcv"])


def validate_date(start_date: str = None) -> str | None:
    """Valide le format de date (YYYY-MM-DD) si fourni."""
    if start_date is None:
        return None
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        return start_date
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Format de date invalide : '{start_date}'. Utiliser YYYY-MM-DD."
        )


@router.get("/daily_by_trading_pair_id")
def get_ohlcv_daily(
    trading_pair_id: int,
    start_date: str = Query(None, description="Date de début (YYYY-MM-DD)"),
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    validated_date = validate_date(start_date)
    return db.ohlcv_daily.get_ohlcv_by_trading_pair(trading_pair_id, validated_date)
```

### Changements appliqués :
1. Ajout d'une fonction `validate_date()` avec gestion explicite de l'erreur
2. Retour d'un HTTP 422 avec message clair en cas de format invalide
3. Application aux 3 endpoints (minute, hourly, daily)

---

## 6. Tests ajoutés

```python
# tests/test_api_endpoints.py — test de validation de date

def test_ohlcv_daily_invalid_date_returns_422(client, auth_headers):
    response = client.get(
        "/ohlcv/daily_by_trading_pair_id",
        params={"trading_pair_id": 1, "start_date": "not-a-date"},
        headers=auth_headers
    )
    assert response.status_code == 422
    assert "Format de date invalide" in response.json()["detail"]


def test_ohlcv_daily_valid_date_returns_200(client, auth_headers):
    response = client.get(
        "/ohlcv/daily_by_trading_pair_id",
        params={"trading_pair_id": 1, "start_date": "2025-01-01"},
        headers=auth_headers
    )
    assert response.status_code == 200
```

---

## 7. Vérification post-fix

```bash
# Après déploiement du fix :
curl -s http://localhost:8003/ohlcv/daily_by_trading_pair_id?trading_pair_id=1&start_date=invalid \
  -H "Authorization: Bearer $TOKEN"
# Résultat attendu : 422 {"detail": "Format de date invalide : 'invalid'. Utiliser YYYY-MM-DD."}
```

---

## 8. Leçons apprises

1. **Toujours valider les entrées utilisateur** — ne jamais transmettre un paramètre brut à la couche BDD
2. **Les erreurs 500 doivent être traquées** — un monitoring applicatif (cf. C20) aurait permis de détecter ce problème plus tôt
3. **Ajouter des tests négatifs** — tester les cas d'erreur, pas seulement les cas nominaux

---

## 9. Références

- **Issue GitHub :** #1 — "Erreur 500 sur /ohlcv avec start_date invalide"
- **Pull Request :** MR associée avec le fix + tests
- **Commit :** fix validé via CI (GitHub Actions)
