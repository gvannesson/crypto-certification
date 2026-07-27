"""Prédiction de la classification (UP/DOWN/STABLE) sur les dernières données."""

import pandas as pd
import numpy as np

from src.model.train_model import train_model
from src.settings import MLSettings, logger


LABELS = MLSettings.classification["labels"]


def make_predictions(pair_classifiers):
    """Pour chaque classifier, entraîne sur toutes les données et prédit la prochaine bougie."""
    for classifier in pair_classifiers:
        df = classifier.df_features
        last_date = df["date"].max()

        feature_cols = train_model(classifier, last_date + pd.Timedelta(hours=1))

        last_row = df[df["date"] == last_date][feature_cols]
        if last_row.empty:
            logger.warning(f"Pas de données pour prédiction {classifier.symbol}")
            continue

        pred_class = classifier.model_instance.predict(last_row)[0]
        pred_proba = classifier.model_instance.predict_proba(last_row)[0]
        confidence = float(np.max(pred_proba))

        if classifier.granularity_type == "hourly":
            next_date = last_date + pd.Timedelta(hours=1)
        else:
            next_date = last_date + pd.Timedelta(days=1)

        prediction = pd.DataFrame([{
            "date": next_date,
            "predicted_class": int(pred_class),
            "predicted_label": LABELS[int(pred_class)],
            "confidence": confidence,
        }])
        classifier.current_predictions = pd.concat(
            [classifier.current_predictions, prediction], ignore_index=True
        )
