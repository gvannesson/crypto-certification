"""Initialisation des classifiers par granularité : instanciation + récupération OHLCV + feature engineering."""

from src.data.fetch_data import fetch_ohlcv_for_classifier
from src.features.build_features import build_features
from src.utils.classes import TradingPairClassifier
from src.utils.functions import get_jwt_token, get_trading_pair_id
from src.settings import HourModelsSettings, DayModelsSettings, logger


def initialize_pair_classifiers_by_granularity(granularity):
    """Crée un TradingPairClassifier par paire configurée, récupère les OHLCV et calcule les features."""
    if granularity == "hour":
        pair_models = HourModelsSettings.pair_models
    elif granularity == "day":
        pair_models = DayModelsSettings.pair_models
    else:
        raise ValueError(f"Granularité invalide : {granularity}")

    token = get_jwt_token()

    pair_classifiers = []
    for pair_model_info in pair_models:
        classifier = TradingPairClassifier(pair_model_info)

        tp_id = get_trading_pair_id(classifier.base_currency, classifier.quote_currency, token)
        classifier.trading_pair_id = tp_id

        logger.info(f"Récupération OHLCV pour {classifier.symbol} (id={tp_id})")
        df = fetch_ohlcv_for_classifier(classifier)
        classifier.df_historical_data = df

        logger.info(f"Construction des features pour {classifier.symbol}")
        classifier.df_features = build_features(df, classifier.granularity_type, classifier.feature_lags)

        pair_classifiers.append(classifier)

    return pair_classifiers
