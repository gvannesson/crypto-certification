import json
import os

import requests

from src.settings import ExtractSettings, logger


def extract_all_cryptodownload():
    os.makedirs(ExtractSettings.JSON_PATH_CD, exist_ok=True)

    for source_name, url in ExtractSettings.JSON_URLS.items():
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            output_file = os.path.join(ExtractSettings.JSON_PATH_CD, f"{source_name}.json")
            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)

            logger.info(f"Données CryptoDownload '{source_name}' sauvegardées dans {output_file} ({len(data)} entrées)")

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération de {source_name} depuis CryptoDownload : {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue pour {source_name} : {e}")
