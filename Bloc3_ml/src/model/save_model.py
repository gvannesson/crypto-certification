"""Sauvegarde des modèles entraînés en fichiers pickle."""

import os
import joblib

from src.settings import DataSettings, logger


def save_classifiers_models(pair_classifiers, granularity):
    """Sauvegarde chaque modèle entraîné sous {models_dir}/{granularity}_models/{SYMBOL}.pkl."""
    dir_path = os.path.join(DataSettings.models_dir_path, f"{granularity}_models")
    os.makedirs(dir_path, exist_ok=True)

    for classifier in pair_classifiers:
        filepath = os.path.join(dir_path, f"{classifier.symbol}.pkl")
        joblib.dump(classifier.model_instance, filepath)
        logger.info(f"Modèle {classifier.symbol} sauvegardé : {filepath}")
