"""Service pour communiquer avec l'API Bloc3 (ml-api)."""

import requests
from django.conf import settings

REQUEST_TIMEOUT = 10


class ForecastService:
    def __init__(self):
        self.base_url = settings.API_E3_BASE_URL
        self._token = None

    def _get_token(self, force_refresh=False):
        if self._token and not force_refresh:
            return self._token
        response = requests.post(
            f"{self.base_url}/api/v1/authentification/login",
            data={"username": settings.E3_SERVICE_USERNAME, "password": settings.E3_SERVICE_PASSWORD},
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            self._token = response.json()["access_token"]
            return self._token
        raise Exception(f"Échec auth Bloc3 : {response.status_code}")

    def get_classification(self, trading_pair_symbol, granularity):
        """Appelle ml-api pour obtenir une classification à la demande (J+1 uniquement)."""
        endpoint = "classify_hourly" if granularity == "hourly" else "classify_daily"
        url = f"{self.base_url}/api/v1/classify/{endpoint}"
        payload = {"trading_pair_symbol": trading_pair_symbol}

        token = self._get_token()
        try:
            response = requests.post(
                url, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=REQUEST_TIMEOUT
            )
        except requests.RequestException as exc:
            return {"error": f"Service ml-api injoignable : {exc}"}

        if response.status_code == 401:
            # Token potentiellement expiré (durée de vie 30 min côté ml-api) : un seul essai
            # de renouvellement plutôt qu'une boucle, pour ne pas masquer un échec d'auth durable.
            token = self._get_token(force_refresh=True)
            try:
                response = requests.post(
                    url, json=payload, headers={"Authorization": f"Bearer {token}"}, timeout=REQUEST_TIMEOUT
                )
            except requests.RequestException as exc:
                return {"error": f"Service ml-api injoignable : {exc}"}

        if response.status_code == 200:
            return response.json()
        return {"error": f"Erreur API : {response.status_code} - {response.text}"}
