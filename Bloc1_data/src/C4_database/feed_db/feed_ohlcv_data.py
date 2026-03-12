import pandas as pd

from src.settings import logger


def save_ohlcv_data_to_db(df: pd.DataFrame, trading_pair, timeframe, db_model):
    try:
        data_to_insert = df.to_dict(orient="records")
        success_count, failed_entries = db_model.create_many(data_to_insert)
        logger.info(f"Insertion réussie de {success_count} données OHLCV pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe}")

        if failed_entries:
            logger.info(f"{len(failed_entries)} lignes non insérées pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe}")

    except Exception as e:
        logger.error(f"Erreur lors de l'insertion des données OHLCV pour la paire {trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe} : {e}")


def save_predictions_to_db(predictions, db, granularity):
    crud_map = {
        "hourly": db.prediction_hourly,
        "daily": db.prediction_daily,
    }

    crud = crud_map.get(granularity)
    if not crud:
        raise ValueError(f"Granularité de prédiction inconnue : {granularity}")

    success_count, failed_entries = crud.create_many(predictions)
    logger.info(f"Insertion réussie de {success_count} prédictions {granularity}")
    return success_count
