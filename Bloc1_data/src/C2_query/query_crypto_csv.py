from src.C4_database.database import with_session
from src.C4_database.models import CryptocurrencyCSV


@with_session
def get_csv_by_trading_pair(trading_pair_id, session=None):
    return session.query(CryptocurrencyCSV).filter(
        CryptocurrencyCSV.trading_pair_id == trading_pair_id,
    ).all()


@with_session
def get_csv_by_exchange(exchange_id, session=None):
    return session.query(CryptocurrencyCSV).filter(
        CryptocurrencyCSV.exchange_id == exchange_id,
    ).all()


@with_session
def get_all_crypto_csvs(session=None):
    return session.query(CryptocurrencyCSV).all()


@with_session
def search_crypto_csvs_by_trading_pair_and_timeframe(trading_pair_id, timeframe, session=None):
    return (session.query(CryptocurrencyCSV)
            .filter(CryptocurrencyCSV.trading_pair_id == trading_pair_id)
            .filter(CryptocurrencyCSV.timeframe.ilike(f"%{timeframe}%"))
            .all())
