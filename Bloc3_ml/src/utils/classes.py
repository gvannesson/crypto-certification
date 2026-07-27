import importlib

import pandas as pd

from src.settings import MLSettings


class TradingPairClassifier:
    """Encapsule un modèle de classification pour une paire de trading donnée."""

    def __init__(self, pair_model_info):
        self.trading_pair_id = None
        self.symbol = pair_model_info["symbol"]
        self.base_currency = pair_model_info["base_currency"]
        self.quote_currency = pair_model_info["quote_currency"]
        self.granularity_type = pair_model_info["granularity_type"]
        self.model_name = pair_model_info["model"]
        self.model_params = pair_model_info.get("params", {})
        self.feature_lags = pair_model_info.get("feature_lags", 24)
        self.model_instance = self._initialize_model()

        self.df_historical_data = None
        self.df_features = None
        self.historical_predictions = pd.DataFrame()
        self.current_predictions = pd.DataFrame()

        if self.granularity_type == "daily":
            self.test_window = 7
            self.test_period_duration = pd.DateOffset(months=6)
        elif self.granularity_type == "hourly":
            self.test_window = 24
            self.test_period_duration = pd.DateOffset(months=1)

    def _initialize_model(self):
        """Instancie dynamiquement le modèle à partir de la config YAML."""
        models_config = MLSettings.models_config
        model_cfg = models_config[self.model_name]
        module = importlib.import_module(model_cfg["module"])
        ModelClass = getattr(module, model_cfg["class"])
        params = {**model_cfg["default_params"], **self.model_params}
        return ModelClass(**params)
