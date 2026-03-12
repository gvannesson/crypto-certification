from src.C4_database.database import with_session
from src.C4_database.models import TradingPair


@with_session
def get_all_trading_pairs(session=None):
    return session.query(TradingPair).all()


@with_session
def get_trading_pair_by_currencies(base_currency_id, quote_currency_id, session=None):
    return session.query(TradingPair).filter(
        TradingPair.base_currency_id == base_currency_id,
        TradingPair.quote_currency_id == quote_currency_id,
    ).first()


@with_session
def get_trading_pair_by_id(pair_id, session=None):
    return session.query(TradingPair).filter(TradingPair.id == pair_id).first()
