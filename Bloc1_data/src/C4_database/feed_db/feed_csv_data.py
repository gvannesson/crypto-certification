import json
import os

import pandas as pd

from src.C4_database.database import Database
from src.settings import logger, LogSettings


def save_csv_data_to_db(df: pd.DataFrame, db, crypto_csv):
    try:
        data_to_insert = df.to_dict(orient="records")
        success_count, failed_entries = db.historical_data.create_many(data_to_insert)
        logger.info(f"Insertion réussie de {success_count} données historiques OHLCV du fichier CSV {crypto_csv.file_url}")

        if failed_entries:
            os.makedirs(LogSettings.LOG_PATH, exist_ok=True)
            error_file = os.path.join(LogSettings.LOG_PATH, f"failed_ohlcv_entries_{crypto_csv.file_url.split('/')[-1].split('.')[0]}.json")
            with open(error_file, "w") as f:
                json.dump(failed_entries, f, default=str, indent=4)
            logger.info(f"{len(failed_entries)} lignes non insérées. Détails dans {error_file}")

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des données historiques OHLCV du CSV {crypto_csv.file_url} : {e}")
