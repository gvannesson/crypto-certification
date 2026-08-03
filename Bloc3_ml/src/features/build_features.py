"""Construction des features (indicateurs techniques, lags, cible) pour la classification."""

import pandas as pd
import pandas_ta as ta
import numpy as np

from src.settings import MLSettings, logger


def build_features(df, granularity_type, feature_lags, include_target=True):
    """Pipeline complet : lags + returns + indicateurs techniques + encodage temporel + variable cible."""
    df = df.copy()
    df = df.sort_values("date").set_index("date")

    df = add_lag_features(df, feature_lags)
    df = add_return_features(df, granularity_type)
    df = add_technical_indicators(df)
    df = add_temporal_features(df, granularity_type)
    if include_target:
        df = add_target(df)
    df = df.dropna(subset=[c for c in df.columns if c != "target"]).reset_index()

    return df


def add_lag_features(df, n_lags):
    """Ajoute des lags autorégressifs sur close, volume_quote, high, low."""
    for col in ["close", "volume_quote", "high", "low"]:
        for lag in range(1, n_lags + 1):
            df[f"{col}_lag_{lag}"] = df[col].shift(lag)
    return df


def add_return_features(df, granularity_type):
    """Ajoute les rendements (pct_change) sur différentes fenêtres."""
    windows = [1, 3, 6]
    if granularity_type == "hourly":
        windows.append(12)
    for w in windows:
        df[f"return_{w}"] = df["close"].pct_change(w)
    return df


def add_technical_indicators(df):
    """Calcule RSI, MACD, Bollinger Bands, SMA, EMA, ATR."""
    df["rsi"] = ta.rsi(df["close"], length=14)

    macd = ta.macd(df["close"], fast=12, slow=26, signal=9)
    if macd is not None:
        df = pd.concat([df, macd], axis=1)

    bbands = ta.bbands(df["close"], length=20, std=2)
    if bbands is not None:
        df = pd.concat([df, bbands], axis=1)

    for period in [7, 14, 50]:
        df[f"sma_{period}"] = ta.sma(df["close"], length=period)

    for period in [12, 26]:
        df[f"ema_{period}"] = ta.ema(df["close"], length=period)

    df["atr"] = ta.atr(df["high"], df["low"], df["close"], length=14)

    return df


def add_temporal_features(df, granularity_type):
    """Extrait des features temporelles de l'index datetime."""
    idx = df.index
    if granularity_type == "hourly":
        df["hour"] = idx.hour
    df["day_of_week"] = idx.dayofweek
    df["day_of_month"] = idx.day
    df["month"] = idx.month
    df["is_weekend"] = (idx.dayofweek >= 5).astype(int)
    return df


def add_target(df):
    """Construit la variable cible ternaire (DOWN=0, STABLE=1, UP=2).

    La cible est la variation de la PROCHAINE bougie (shift -1),
    pour que le modèle apprenne à prédire le futur et non le passé.
    """
    seuil = MLSettings.classification["seuil"]
    df["variation"] = df["close"].pct_change(1).shift(-1)
    df["target"] = pd.cut(
        df["variation"],
        bins=[-float("inf"), -seuil, seuil, float("inf")],
        labels=[0, 1, 2],
    ).astype(float)
    df = df.drop(columns=["variation"])
    return df
