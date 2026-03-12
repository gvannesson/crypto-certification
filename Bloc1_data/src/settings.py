import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s")
logger = logging.getLogger("Bloc1_data")

BASE_DIR = Path(__file__).parent.parent
load_dotenv()


def load_yaml_config(filename):
    config_path = BASE_DIR / "config" / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


try:
    EXTRACT_CONFIG = load_yaml_config("extract_config.yaml")
    UPDATE_CONFIG = load_yaml_config("update_config.yaml")
except FileNotFoundError as e:
    print(f"Warning: {e}")


class ExtractSettings:
    JSON_PATH_CD = EXTRACT_CONFIG["save_dir"]["cryptodownload"]
    JSON_PATH_CMC = EXTRACT_CONFIG["save_dir"]["coinmarketcap"]
    JSON_URLS = EXTRACT_CONFIG["cryptodownload"]["json_urls"]
    CMC_MAPS = EXTRACT_CONFIG["coinmarketcap"]["maps"]
    TRADING_PAIRS = EXTRACT_CONFIG["trading_pairs"]


class SecretSettings:
    CMC_API_KEY = os.getenv("CMC_API_KEY")
    API_SECRET_KEY = os.getenv("API_E1_SECRET_KEY")
    API_ALGORITHM = os.getenv("API_E1_ALGORITHM")
    API_USERNAME = os.getenv("API_E1_SCRIPT_USERNAME")
    API_PASSWORD = os.getenv("API_E1_SCRIPT_PASSWORD")
    API_ROLE = os.getenv("API_E1_SCRIPT_ROLE")
    DB_USERNAME = os.getenv("DB_USERNAME")
    DB_PASSWORD = os.getenv("DB_PASSWORD")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")


class UpdateSettings:
    BINANCE_OHLCV_URL = UPDATE_CONFIG["binance_ohlcv_url"]
    TRADING_PAIRS = UPDATE_CONFIG["trading_pairs"]


class LogSettings:
    LOG_PATH = os.path.join(BASE_DIR, "data/logs")
