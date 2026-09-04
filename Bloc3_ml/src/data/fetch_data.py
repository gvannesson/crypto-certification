import requests
import pandas as pd

from src.settings import DataSettings
from src.utils.functions import get_jwt_token


def fetch_ohlcv_for_classifier(classifier):
    """Récupère les données OHLCV depuis l'API Bloc1 pour un classifier donné."""
    token = get_jwt_token()
    if not token:
        raise Exception("Échec de la récupération du token JWT.")

    granularity = "hourly" if classifier.granularity_type == "hourly" else "daily"
    url = DataSettings.E1_ohlcv_urls[granularity]
    headers = {"Authorization": f"Bearer {token}"}
    params = {"trading_pair_id": classifier.trading_pair_id}

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        df = pd.DataFrame(response.json())
        df["date"] = pd.to_datetime(df["date"])
        return df
    else:
        raise Exception(f"Échec OHLCV : {response.status_code} - {response.text}")
