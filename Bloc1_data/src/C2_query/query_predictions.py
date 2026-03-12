from src.C4_database.database import with_session
from src.C4_database.models import PredictionHourly, PredictionDaily
from src.utils.functions import validate_date


@with_session
def get_predictions_hourly_by_pair(trading_pair_id, start_date=None, session=None):
    query = session.query(PredictionHourly).filter(PredictionHourly.trading_pair_id == trading_pair_id)
    if start_date:
        validated = validate_date(start_date)
        if validated:
            query = query.filter(PredictionHourly.date >= validated)
    return query.order_by(PredictionHourly.date.asc()).all()


@with_session
def get_last_prediction_hourly(trading_pair_id, session=None):
    return session.query(PredictionHourly).filter(
        PredictionHourly.trading_pair_id == trading_pair_id,
    ).order_by(PredictionHourly.date.desc()).first()


@with_session
def get_predictions_daily_by_pair(trading_pair_id, start_date=None, session=None):
    query = session.query(PredictionDaily).filter(PredictionDaily.trading_pair_id == trading_pair_id)
    if start_date:
        validated = validate_date(start_date)
        if validated:
            query = query.filter(PredictionDaily.date >= validated)
    return query.order_by(PredictionDaily.date.asc()).all()


@with_session
def get_last_prediction_daily(trading_pair_id, session=None):
    return session.query(PredictionDaily).filter(
        PredictionDaily.trading_pair_id == trading_pair_id,
    ).order_by(PredictionDaily.date.desc()).first()
