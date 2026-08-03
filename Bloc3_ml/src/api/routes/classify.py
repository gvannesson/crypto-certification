"""Endpoints de classification à la demande."""

import numpy as np
import pandas as pd
from fastapi import APIRouter, Depends, Body

from src.api.utils.deps import get_current_user
from src.api.utils.classes import ClassifyRequest
from src.api.utils.functions import load_model, fetch_recent_ohlcv, build_features_for_prediction
from src.settings import MLSettings

router = APIRouter(prefix="/classify", tags=["classify"])

LABELS = MLSettings.classification["labels"]


@router.post("/classify_hourly")
def classify_hourly(payload: ClassifyRequest = Body(...), current_user=Depends(get_current_user)):
    """Classification horaire à la demande (H+1)."""
    model = load_model(payload.trading_pair_symbol, "hour_models")
    prediction = _run_classification(model, payload, granularity="hourly", freq_delta=pd.Timedelta(hours=1))
    return {"trading_pair_symbol": payload.trading_pair_symbol, "predictions": prediction}


@router.post("/classify_daily")
def classify_daily(payload: ClassifyRequest = Body(...), current_user=Depends(get_current_user)):
    """Classification journalière à la demande (J+1)."""
    model = load_model(payload.trading_pair_symbol, "day_models")
    prediction = _run_classification(model, payload, granularity="daily", freq_delta=pd.Timedelta(days=1))
    return {"trading_pair_symbol": payload.trading_pair_symbol, "predictions": prediction}


def _run_classification(model, payload, granularity, freq_delta):
    """Charge les features du dernier pas de temps connu et prédit le suivant."""
    df = fetch_recent_ohlcv(payload.trading_pair_symbol, granularity)
    feature_df = build_features_for_prediction(df, granularity)

    feature_cols = [c for c in feature_df.columns if c not in ["date", "target", "trading_pair_id"]]
    trained_features = model.get_booster().feature_names
    if trained_features:
        feature_cols = [c for c in trained_features if c in feature_cols]
    last_date = feature_df["date"].max()

    row = feature_df[feature_df["date"] == last_date][feature_cols]
    if row.empty:
        return []

    pred_proba = model.predict_proba(row)[0]
    pred_class = int(np.argmax(pred_proba))
    confidence = float(np.max(pred_proba))
    next_date = last_date + freq_delta

    return [{
        "date": str(next_date),
        "predicted_class": pred_class,
        "predicted_label": LABELS[pred_class],
        "confidence": round(confidence, 4),
    }]
