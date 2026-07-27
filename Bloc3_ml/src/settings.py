import logging
import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s - %(message)s")
logger = logging.getLogger("Bloc3_ml")

BASE_DIR = Path(__file__).parent.parent
load_dotenv()


def load_yaml_config(filename):
    config_path = BASE_DIR / "config" / filename
    if not config_path.exists():
        raise FileNotFoundError(f"Fichier de configuration non trouvé: {config_path}")
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


try:
    DATA_CONFIG = load_yaml_config("data_config.yaml")
    ML_CONFIG = load_yaml_config("ml_config.yaml")
    HOUR_MODELS_CONFIG = load_yaml_config("hour_models_config.yaml")
    DAY_MODELS_CONFIG = load_yaml_config("day_models_config.yaml")
except FileNotFoundError as e:
    print(f"Warning: {e}")


E1_API_BASE_URL = os.getenv("API_E1_BASE_URL", "http://localhost:8001")
E3_API_BASE_URL = os.getenv("API_E3_BASE_URL", "http://localhost:8002")


class DataSettings:
    E1_login_url = f"{E1_API_BASE_URL}{DATA_CONFIG['E1_api_endpoints']['login']}"
    E1_trading_pair_url = f"{E1_API_BASE_URL}{DATA_CONFIG['E1_api_endpoints']['trading_pair_by_symbols']}"
    E1_ohlcv_urls = {k: f"{E1_API_BASE_URL}{v}" for k, v in DATA_CONFIG["E1_api_endpoints"]["ohlcv"].items()}
    E1_post_predictions_urls = {k: f"{E1_API_BASE_URL}{v}" for k, v in DATA_CONFIG["E1_api_endpoints"]["post_predictions"].items()}
    models_dir_path = os.getenv("MODELS_DIR_PATH", "models")
    trading_pairs = DATA_CONFIG["trading_pairs"]


class MLSettings:
    models_config = ML_CONFIG["models_config"]
    classification = ML_CONFIG["classification"]
    dates_by_granularity = ML_CONFIG["dates_by_granularity"]
    ml_flow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")


class HourModelsSettings:
    pair_models = HOUR_MODELS_CONFIG["pair_models"]


class DayModelsSettings:
    pair_models = DAY_MODELS_CONFIG["pair_models"]


class SecretSettings:
    E1_USERNAME = os.getenv("API_E1_SCRIPT_USERNAME")
    E1_PASSWORD = os.getenv("API_E1_SCRIPT_PASSWORD")
    E3_SECRET_KEY = os.getenv("API_E3_SECRET_KEY")
    E3_ALGORITHM = os.getenv("API_E3_ALGORITHM", "HS256")
    E3_USERNAME = os.getenv("API_E3_USERNAME")
    E3_PASSWORD = os.getenv("API_E3_PASSWORD")
