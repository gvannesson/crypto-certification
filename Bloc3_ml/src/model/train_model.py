"""Entraînement du modèle de classification."""

import pandas as pd

from src.settings import logger


def train_model(classifier, train_end_date):
    """Entraîne le modèle du classifier sur les données jusqu'à train_end_date (exclu)."""
    df = classifier.df_features
    train_data = df[df["date"] < train_end_date]

    feature_cols = [c for c in train_data.columns if c not in ["date", "target", "trading_pair_id"]]
    X_train = train_data[feature_cols]
    y_train = train_data["target"]

    classifier.model_instance.fit(X_train, y_train)
    return feature_cols
