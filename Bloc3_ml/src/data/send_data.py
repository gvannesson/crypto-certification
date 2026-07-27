import requests

from src.settings import DataSettings, logger
from src.utils.functions import get_jwt_token


def save_predictions_to_db(pair_classifiers):
    """Envoie les prédictions courantes de chaque classifier vers l'API Bloc1."""
    token = get_jwt_token()
    if not token:
        raise Exception("Échec de la récupération du token JWT.")

    for classifier in pair_classifiers:
        granularity = "hourly" if classifier.granularity_type == "hourly" else "daily"
        url = DataSettings.E1_post_predictions_urls[granularity]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        for _, row in classifier.current_predictions.iterrows():
            payload = {
                "trading_pair_id": classifier.trading_pair_id,
                "date": str(row["date"]),
                "predicted_class": int(row["predicted_class"]),
                "predicted_label": row["predicted_label"],
                "confidence": float(row["confidence"]) if "confidence" in row else None,
                "model_name": classifier.model_name,
            }
            response = requests.post(url, json=payload, headers=headers)
            if response.status_code != 200:
                logger.error(f"Erreur POST prédiction : {response.status_code} - {response.text}")
