"""Pipeline principal : initialise les classifiers, évalue, prédit, envoie et sauvegarde."""

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).parent
sys.path.append(str(ROOT_DIR))

from src.model.initiate_classifier import initialize_pair_classifiers_by_granularity
from src.model.predict_model import make_predictions
from src.model.save_model import save_classifiers_models
from src.monitoring.monitor_training import monitor_trainings
from src.data.send_data import save_predictions_to_db
from src.settings import logger


def parse_args():
    parser = argparse.ArgumentParser(description="Pipeline ML de classification de tendance")
    parser.add_argument("--granularity", choices=["hour", "day"], required=True)
    return parser.parse_args()


def main():
    args = parse_args()

    logger.info(f"Démarrage du pipeline ML ({args.granularity})")

    logger.info("Initialisation des classifiers")
    pair_classifiers = initialize_pair_classifiers_by_granularity(args.granularity)

    logger.info("Évaluation et monitoring MLflow")
    monitor_trainings(pair_classifiers, args.granularity)

    logger.info("Prédictions sur les données courantes")
    make_predictions(pair_classifiers)

    logger.info("Envoi des prédictions vers Bloc1 API")
    save_predictions_to_db(pair_classifiers)

    logger.info("Sauvegarde des modèles")
    save_classifiers_models(pair_classifiers, args.granularity)

    logger.info(f"Pipeline ML terminé ({args.granularity})")


if __name__ == "__main__":
    main()
