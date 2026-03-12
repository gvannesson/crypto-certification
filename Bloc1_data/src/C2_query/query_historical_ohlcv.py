from src.C4_database.database import with_session
from src.C4_database.models import CryptocurrencyCSV, CSVHistoricalData, TradingPair


@with_session
def get_historical_data_by_csv(csv_file_id, session=None):
    return session.query(CSVHistoricalData).filter(
        CSVHistoricalData.csv_file_id == csv_file_id,
    ).order_by(CSVHistoricalData.date.asc()).all()


@with_session
def get_all_historical_data(session=None):
    return session.query(CSVHistoricalData).all()


@with_session
def get_pairs_and_timeframes_from_historical_data(session=None):
    return (
        session.query(TradingPair, CryptocurrencyCSV.timeframe)
        .join(CryptocurrencyCSV, CryptocurrencyCSV.trading_pair_id == TradingPair.id)
        .join(CSVHistoricalData, CSVHistoricalData.csv_file_id == CryptocurrencyCSV.id)
        .distinct()
        .all()
    )


@with_session
def get_historical_ohlcv_by_pair_id_and_timeframe(trading_pair_id, timeframe, session=None):
    return (
        session.query(CSVHistoricalData)
        .join(CryptocurrencyCSV)
        .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
        .filter(CryptocurrencyCSV.timeframe == timeframe)
        .all()
    )
