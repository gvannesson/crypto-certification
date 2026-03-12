from src.C4_database.database import with_session
from src.C4_database.models import OHLCVDaily
from src.utils.functions import validate_date


@with_session
def get_ohlcv_daily_by_pair(trading_pair_id, start_date=None, session=None):
    query = session.query(OHLCVDaily).filter(OHLCVDaily.trading_pair_id == trading_pair_id)
    if start_date:
        validated = validate_date(start_date)
        if validated:
            query = query.filter(OHLCVDaily.date >= validated)
    return query.order_by(OHLCVDaily.date.asc()).all()


@with_session
def get_last_ohlcv_daily(trading_pair_id, session=None):
    return session.query(OHLCVDaily).filter(
        OHLCVDaily.trading_pair_id == trading_pair_id,
    ).order_by(OHLCVDaily.date.desc()).first()
