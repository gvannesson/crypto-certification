"""Endpoints de classification à la demande."""

import os

import numpy as np
import pandas as pd
import requests
from fastapi import APIRouter, Depends, HTTPException, Body

from src.api.utils.deps import get_current_user
from src.api.utils.classes import ClassifyRequest
from src.api.utils.functions import load_model, fetch_recent_ohlcv, build_features_for_prediction
from src.settings import MLSettings

router = APIRouter(prefix="/classify", tags=["classify"])

LABELS = MLSettings.classification["labels"]


@router.post("/classify_hourly")
def classify_hourly(payload: ClassifyRequest = Body(...), current_user=Depends(get_current_user)):
    """Classification horaire à la demande."""
    if payload.num_pred < 1 or payload.num_pred > 24:
        raise HTTPException(status_code=400, detail="num_pred doit être entre 1 et 24")

    model = load_model(payload.trading_pair_symbol, "hour_models")
    predictions = _run_classification(model, payload, granularity="hourly", freq_delta=pd.Timedelta(hours=1))
    return {"trading_pair_symbol": payload.trading_pair_symbol, "num_pred": payload.num_pred, "predictions": predictions}


@router.post("/classify_daily")
def classify_daily(payload: ClassifyRequest = Body(...), current_user=Depends(get_current_user)):
    """Classification journalière à la demande."""
    if payload.num_pred < 1 or payload.num_pred > 7:
        raise HTTPException(status_code=400, detail="num_pred doit être entre 1 et 7")

    model = load_model(payload.trading_pair_symbol, "day_models")
    predictions = _run_classification(model, payload, granularity="daily", freq_delta=pd.Timedelta(days=1))
    return {"trading_pair_symbol": payload.trading_pair_symbol, "num_pred": payload.num_pred, "predictions": predictions}


def _run_classification(model, payload, granularity, freq_delta):
    """Logique commune : charge les features et prédit num_pred pas de temps."""
    df = fetch_recent_ohlcv(payload.trading_pair_symbol, granularity)
    feature_df = build_features_for_prediction(df, granularity)

    feature_cols = [c for c in feature_df.columns if c not in ["date", "target", "trading_pair_id"]]
    last_date = feature_df["date"].max()

    predictions = []
    for i in range(payload.num_pred):
        row = feature_df[feature_df["date"] == last_date][feature_cols]
        if row.empty:
            break
        pred_class = int(model.predict(row)[0])
        pred_proba = model.predict_proba(row)[0]
        confidence = float(np.max(pred_proba))
        next_date = last_date + freq_delta * (i + 1)

        predictions.append({
            "date": str(next_date),
            "predicted_class": pred_class,
            "predicted_label": LABELS[pred_class],
            "confidence": round(confidence, 4),
        })

    return predictions
