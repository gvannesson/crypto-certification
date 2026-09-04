
import requests
import pandas as pd

from src.settings import DataSettings, SecretSettings, MLSettings, logger


def get_jwt_token():
    """Obtient un JWT depuis l'API Bloc1 avec le compte de service."""
    response = requests.post(
        DataSettings.E1_login_url,
        data={"username": SecretSettings.E1_USERNAME, "password": SecretSettings.E1_PASSWORD},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    logger.error(f"Échec auth E1 : {response.status_code} - {response.text}")
    return None


def get_trading_pair_id(base_symbol, quote_symbol, token):
    """Récupère l'id d'une trading pair via l'API Bloc1."""
    response = requests.get(
        DataSettings.E1_trading_pair_url,
        params={"base": base_symbol, "quote": quote_symbol},
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code == 200:
        return response.json()["id"]
    logger.error(f"Échec récup trading pair : {response.status_code}")
    return None


def generate_test_periods(classifier):
    """Génère les périodes de test glissantes pour l'évaluation."""
    dates = MLSettings.dates_by_granularity[
        "daily" if classifier.granularity_type == "daily" else "hourly"
    ]
    test_start = pd.to_datetime(dates["test_start"])
    test_end = pd.to_datetime(dates["test_end"])

    periods = {"test_start": [], "test_end": []}
    current = test_start

    while current < test_end:
        period_end = current + classifier.test_period_duration
        if period_end > test_end:
            period_end = test_end
        periods["test_start"].append(current)
        periods["test_end"].append(period_end)
        current = period_end

    return periods
