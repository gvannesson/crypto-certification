"""Service pour communiquer avec l'API Bloc3 (ml-api)."""

import requests
from django.conf import settings


class ForecastService:
    def __init__(self):
        self.base_url = settings.API_E3_BASE_URL
        self._token = None

    def _get_token(self):
        if self._token:
            return self._token
        response = requests.post(
            f"{self.base_url}/api/v1/authentification/login",
            data={"username": settings.E3_SERVICE_USERNAME, "password": settings.E3_SERVICE_PASSWORD},
        )
        if response.status_code == 200:
            self._token = response.json()["access_token"]
            return self._token
        raise Exception(f"Échec auth Bloc3 : {response.status_code}")

    def get_classification(self, trading_pair_symbol, granularity):
        """Appelle ml-api pour obtenir une classification à la demande (J+1 uniquement)."""
        token = self._get_token()
        endpoint = "classify_hourly" if granularity == "hourly" else "classify_daily"
        response = requests.post(
            f"{self.base_url}/api/v1/classify/{endpoint}",
            json={"trading_pair_symbol": trading_pair_symbol},
            headers={"Authorization": f"Bearer {token}"},
        )
        if response.status_code == 200:
            return response.json()
        return {"error": f"Erreur API : {response.status_code} - {response.text}"}
