"""Service pour communiquer avec l'API Bloc1 (data-api)."""

import requests
from django.conf import settings

REQUEST_TIMEOUT = 10


class DashboardService:
    def __init__(self):
        self.base_url = settings.API_E1_BASE_URL
        self._token = None

    def _get_token(self):
        if self._token:
            return self._token
        response = requests.post(
            f"{self.base_url}/api/v1/authentification/login",
            data={"username": settings.E1_SERVICE_USERNAME, "password": settings.E1_SERVICE_PASSWORD},
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            self._token = response.json()["access_token"]
            return self._token
        raise Exception(f"Échec auth Bloc1 : {response.status_code}")

    def _headers(self):
        return {"Authorization": f"Bearer {self._get_token()}"}

    def get_trading_pair(self, base_symbol, quote_symbol):
        response = requests.get(
            f"{self.base_url}/api/v1/trading_pairs/trading_pair_by_currency_symbols",
            params={"base": base_symbol, "quote": quote_symbol},
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()
        return None

    def get_ohlcv(self, trading_pair_id, granularity="daily"):
        endpoint = f"hourly_by_trading_pair_id" if granularity == "hourly" else "daily_by_trading_pair_id"
        response = requests.get(
            f"{self.base_url}/api/v1/ohlcv/{endpoint}",
            params={"trading_pair_id": trading_pair_id},
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()
        return []

    def get_predictions(self, trading_pair_id, granularity="daily"):
        endpoint = "hourly_by_trading_pair_id" if granularity == "hourly" else "daily_by_trading_pair_id"
        response = requests.get(
            f"{self.base_url}/api/v1/predictions/{endpoint}/{trading_pair_id}",
            headers=self._headers(),
            timeout=REQUEST_TIMEOUT,
        )
        if response.status_code == 200:
            return response.json()
        return []
