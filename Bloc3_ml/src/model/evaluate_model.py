"""Évaluation des performances du modèle de classification sur des périodes de test glissantes."""

import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

from src.model.train_model import train_model
from src.utils.functions import generate_test_periods
from src.settings import MLSettings, logger

LABELS = MLSettings.classification["labels"]


def evaluate_classifier(classifier):
    """Évalue le classifier sur des fenêtres de test glissantes. Retourne les métriques agrégées."""
    test_periods = generate_test_periods(classifier)
    df = classifier.df_features

    all_y_true = []
    all_y_pred = []

    for start, end in zip(test_periods["test_start"], test_periods["test_end"]):
        feature_cols = train_model(classifier, start)

        test_data = df[(df["date"] >= start) & (df["date"] < end)]
        if test_data.empty:
            continue

        X_test = test_data[feature_cols]
        y_test = test_data["target"]
        y_pred = classifier.model_instance.predict(X_test)

        all_y_true.extend(y_test.tolist())
        all_y_pred.extend(y_pred.tolist())

        pred_df = pd.DataFrame({
            "date": test_data["date"].values,
            "y_true": y_test.values,
            "y_pred": y_pred,
        })
        classifier.historical_predictions = pd.concat(
            [classifier.historical_predictions, pred_df], ignore_index=True
        )

    metrics = compute_metrics(all_y_true, all_y_pred)
    return metrics


def compute_metrics(y_true, y_pred):
    """Calcule accuracy, F1 macro, F1 par classe, direction accuracy."""
    accuracy = accuracy_score(y_true, y_pred)
    f1_macro = f1_score(y_true, y_pred, average="macro", zero_division=0)
    f1_per_class = f1_score(y_true, y_pred, average=None, labels=[0, 1, 2], zero_division=0)

    y_true_arr = np.array(y_true)
    y_pred_arr = np.array(y_pred)
    mask = (y_true_arr != 1) | (y_pred_arr != 1)
    if mask.sum() > 0:
        direction_accuracy = ((y_true_arr[mask] == y_pred_arr[mask]).sum()) / mask.sum()
    else:
        direction_accuracy = 0.0

    return {
        "accuracy": round(accuracy, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_down": round(float(f1_per_class[0]), 4),
        "f1_stable": round(float(f1_per_class[1]), 4),
        "f1_up": round(float(f1_per_class[2]), 4),
        "direction_accuracy": round(direction_accuracy, 4),
    }
