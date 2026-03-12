from src.C4_database.database import with_session
from src.C4_database.models import OHLCVMinute
from src.utils.functions import validate_date


@with_session
def get_ohlcv_minute_by_pair(trading_pair_id, start_date=None, session=None):
    query = session.query(OHLCVMinute).filter(OHLCVMinute.trading_pair_id == trading_pair_id)
    if start_date:
        validated = validate_date(start_date)
        if validated:
            query = query.filter(OHLCVMinute.date >= validated)
    return query.order_by(OHLCVMinute.date.asc()).all()


@with_session
def get_last_ohlcv_minute(trading_pair_id, session=None):
    return session.query(OHLCVMinute).filter(
        OHLCVMinute.trading_pair_id == trading_pair_id,
    ).order_by(OHLCVMinute.date.desc()).first()
