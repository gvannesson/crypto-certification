import json
import os

import requests

from src.settings import ExtractSettings, SecretSettings, logger


def extract_all_coinmarketcap():
    headers = {
        "Accept": "application/json",
        "X-CMC_PRO_API_KEY": SecretSettings.CMC_API_KEY,
    }

    os.makedirs(ExtractSettings.JSON_PATH_CMC, exist_ok=True)

    for map_name, url in ExtractSettings.CMC_MAPS.items():
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            output_file = os.path.join(ExtractSettings.JSON_PATH_CMC, f"{map_name}.json")
            with open(output_file, "w") as f:
                json.dump(data, f, indent=4)

            logger.info(f"Données CoinMarketCap '{map_name}' sauvegardées dans {output_file} ({len(data.get('data', []))} entrées)")

        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur lors de la récupération de {map_name} depuis CoinMarketCap : {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue pour {map_name} : {e}")
