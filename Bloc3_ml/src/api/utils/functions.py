"""Fonctions utilitaires pour l'API ML : chargement de modèles et préparation des features."""

import os
import joblib

import requests
import pandas as pd
from fastapi import HTTPException

from src.settings import DataSettings, SecretSettings
from src.features.build_features import build_features


def load_model(symbol: str, granularity_folder: str):
    """Charge un modèle pickle depuis le dossier de modèles."""
    model_path = os.path.join(DataSettings.models_dir_path, granularity_folder, f"{symbol}.pkl")
    if not os.path.exists(model_path):
        raise HTTPException(status_code=404, detail=f"Aucun modèle entraîné pour '{symbol}'.")
    return joblib.load(model_path)


def fetch_recent_ohlcv(symbol: str, granularity: str):
    """Récupère les OHLCV récentes depuis l'API Bloc1 pour le calcul de features."""
    token = _get_e1_token()
    pair_info = symbol.split("-")
    base, quote = pair_info[0], pair_info[1]

    tp_response = requests.get(
        DataSettings.E1_trading_pair_url,
        params={"base": base, "quote": quote},
        headers={"Authorization": f"Bearer {token}"},
    )
    if tp_response.status_code != 200:
        raise HTTPException(status_code=404, detail=f"Paire de trading introuvable : '{symbol}'.")

    tp_id = tp_response.json()["id"]
    ohlcv_url = DataSettings.E1_ohlcv_urls[granularity]
    response = requests.get(
        ohlcv_url,
        params={"trading_pair_id": tp_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    if response.status_code != 200:
        raise Exception(f"Échec OHLCV : {response.status_code}")

    df = pd.DataFrame(response.json())
    df["date"] = pd.to_datetime(df["date"])
    return df


def build_features_for_prediction(df, granularity):
    """Construit les features à partir des OHLCV pour la prédiction (sans cible)."""
    lags = 24 if granularity == "hourly" else 7
    return build_features(df, granularity, lags, include_target=False)


def _get_e1_token():
    """Obtient un JWT depuis l'API Bloc1."""
    response = requests.post(
        DataSettings.E1_login_url,
        data={"username": SecretSettings.E1_USERNAME, "password": SecretSettings.E1_PASSWORD},
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    raise Exception(f"Échec auth E1 : {response.status_code}")
