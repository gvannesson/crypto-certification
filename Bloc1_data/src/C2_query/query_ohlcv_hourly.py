from src.C4_database.database import with_session
from src.C4_database.models import OHLCVHourly
from src.utils.functions import validate_date


@with_session
def get_ohlcv_hourly_by_pair(trading_pair_id, start_date=None, session=None):
    query = session.query(OHLCVHourly).filter(OHLCVHourly.trading_pair_id == trading_pair_id)
    if start_date:
        validated = validate_date(start_date)
        if validated:
            query = query.filter(OHLCVHourly.date >= validated)
    return query.order_by(OHLCVHourly.date.asc()).all()


@with_session
def get_last_ohlcv_hourly(trading_pair_id, session=None):
    return session.query(OHLCVHourly).filter(
        OHLCVHourly.trading_pair_id == trading_pair_id,
    ).order_by(OHLCVHourly.date.desc()).first()
