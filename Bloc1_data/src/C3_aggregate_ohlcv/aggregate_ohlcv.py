import numpy as np
import pandas as pd

from src.C2_query.query_historical_ohlcv import get_pairs_and_timeframes_from_historical_data, get_historical_ohlcv_by_pair_id_and_timeframe
from src.C4_database.database import Database
from src.C4_database.feed_db.feed_ohlcv_data import save_ohlcv_data_to_db
from src.settings import logger


def aggregate_all_ohlcv():
    with Database() as db:

        pairs_and_timeframes = get_pairs_and_timeframes_from_historical_data(session=db.session)
        if not pairs_and_timeframes:
            logger.warning("Aucune paire de trading trouvée dans les données historiques OHLCV")
            return

        for trading_pair, timeframe in pairs_and_timeframes:
            ohlcv_data = get_historical_ohlcv_by_pair_id_and_timeframe(trading_pair.id, timeframe, session=db.session)
            aggregated_df = aggregate_ohlcv_data(ohlcv_data, trading_pair, timeframe)

            if aggregated_df is None:
                continue

            if timeframe == "day":
                db_model = db.ohlcv_daily
            elif timeframe == "hour":
                db_model = db.ohlcv_hourly
            else:
                logger.warning(f"Timeframe inconnu ou non supporté : {timeframe}")
                continue

            save_ohlcv_data_to_db(aggregated_df, trading_pair, timeframe, db_model)


def aggregate_ohlcv_data(ohlcv_data, trading_pair, timeframe):
    """Agrège et normalise les enregistrements OHLCV bruts (CSVHistoricalData) pour une paire & un timeframe.

    Consolide plusieurs lignes brutes sur une même date en une seule observation normalisée
    par (trading_pair_id, date). Utilise la moyenne pondérée par le volume pour open/close
    si volume > 0, sinon moyenne simple.
    """

    try:
        records = [(data.date, data.open, data.high, data.low, data.close, data.volume_quote)
                   for data in ohlcv_data]

        df = pd.DataFrame.from_records(records, columns=["date", "open", "high", "low", "close", "volume_quote"])
        df["trading_pair_id"] = trading_pair.id

        df["weighted_open"] = df["open"] * df["volume_quote"]
        df["weighted_close"] = df["close"] * df["volume_quote"]

        aggregated_df = df.groupby(["trading_pair_id", "date"], as_index=False).agg({
            "weighted_open": "sum",
            "weighted_close": "sum",
            "open": "mean",
            "close": "mean",
            "volume_quote": "sum",
            "high": "max",
            "low": "min"
        })

        aggregated_df["open"] = np.where(
            aggregated_df["volume_quote"] == 0,
            aggregated_df["open"],
            aggregated_df["weighted_open"] / aggregated_df["volume_quote"]
        )
        aggregated_df["close"] = np.where(
            aggregated_df["volume_quote"] == 0,
            aggregated_df["close"],
            aggregated_df["weighted_close"] / aggregated_df["volume_quote"]
        )

        aggregated_df = aggregated_df.drop(columns=["weighted_open", "weighted_close"])

        return aggregated_df

    except Exception as e:
        logger.error(
            f"Erreur lors de l'agrégation des données OHLCV pour la paire "
            f"{trading_pair.base_currency.symbol}/{trading_pair.quote_currency.symbol} et le timeframe {timeframe}: {e}"
        )
        return None
