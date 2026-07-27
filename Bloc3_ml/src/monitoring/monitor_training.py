"""Logging des performances d'entraînement dans MLflow."""

import mlflow
import pandas as pd

from src.model.evaluate_model import evaluate_classifier
from src.settings import MLSettings, logger


def monitor_trainings(pair_classifiers, granularity):
    """Évalue chaque classifier et log les résultats dans MLflow."""
    if granularity == "hour":
        training_date = pd.Timestamp.utcnow().replace(minute=0, second=0, microsecond=0)
    else:
        training_date = pd.Timestamp.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    mlflow.set_tracking_uri(MLSettings.ml_flow_tracking_uri)

    for classifier in pair_classifiers:
        experiment_name = f"{classifier.symbol}_training_monitoring"
        mlflow.set_experiment(experiment_name)

        with mlflow.start_run(run_name=f"{classifier.granularity_type}_{training_date}"):
            mlflow.set_tag("symbol", classifier.symbol)
            mlflow.set_tag("model_name", classifier.model_name)
            mlflow.set_tag("granularity", classifier.granularity_type)

            mlflow.log_params({
                "trading_pair_symbol": classifier.symbol,
                "granularity": classifier.granularity_type,
                "model_name": classifier.model_name,
                "model_params": str(classifier.model_params),
                "training_date": str(training_date),
                "seuil_classification": MLSettings.classification["seuil"],
            })

            logger.info(f"Évaluation de {classifier.symbol} ({classifier.model_name})")
            metrics = evaluate_classifier(classifier)

            mlflow.log_metrics(metrics)
            logger.info(f"Métriques {classifier.symbol} : {metrics}")
