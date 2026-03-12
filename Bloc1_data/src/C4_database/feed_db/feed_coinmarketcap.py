import json
import os
from pathlib import Path

from src.C4_database.database import Database
from src.settings import ExtractSettings, logger, LogSettings


def process_all_cmc_json():
    files_dir = Path(ExtractSettings.JSON_PATH_CMC)

    for file in files_dir.iterdir():
        if file.suffix == ".json":
            if "crypto" in file.stem or "fiat" in file.stem:
                process_currency_json(file, type="crypto" if "crypto" in file.stem else "fiat")
            elif "exchange" in file.stem:
                process_exchange_json(file)


def process_currency_json(file, type):
    try:
        with Database() as db:
            with open(file, "r") as f:
                json_data = json.load(f)

            items = []
            for data in json_data["data"]:
                items.append({
                    "name": data["name"],
                    "symbol": data["symbol"],
                    "slug": data["slug"] if type == "crypto" else None,
                    "sign": data["sign"] if type == "fiat" else None,
                    "rank": data["rank"] if type == "crypto" else None,
                    "type": type,
                })

            success_count, failed_entries = db.currencies.create_many(items)
            logger.info(f"Insertion réussie de {success_count} {type} dans la base de données")

            if failed_entries:
                os.makedirs(LogSettings.LOG_PATH, exist_ok=True)
                error_file = os.path.join(LogSettings.LOG_PATH, f"failed_{type}_insertion.json")
                with open(error_file, "w") as f:
                    json.dump(failed_entries, f, indent=4)
                logger.info(f"{len(failed_entries)} {type} non insérées en raison de doublons ou d'erreurs. Détails dans {error_file}")

    except Exception as e:
        logger.error(f"Erreur pendant le traitement des données : {e}")


def process_exchange_json(file):
    try:
        with Database() as db:
            with open(file, "r") as f:
                json_data = json.load(f)

            items = []
            for data in json_data["data"]:
                items.append({
                    "name": data["name"],
                    "slug": data["slug"],
                })

            success_count, failed_entries = db.exchanges.create_many(items)
            logger.info(f"Insertion réussie de {success_count} plateformes d'échanges dans la base de données")

            if failed_entries:
                os.makedirs(LogSettings.LOG_PATH, exist_ok=True)
                error_file = os.path.join(LogSettings.LOG_PATH, "failed_exchange_insertion.json")
                with open(error_file, "w") as f:
                    json.dump(failed_entries, f, indent=4)
                logger.info(f"{len(failed_entries)} plateformes non insérées. Détails dans {error_file}")

    except Exception as e:
        logger.error(f"Erreur pendant le traitement des données : {e}")
