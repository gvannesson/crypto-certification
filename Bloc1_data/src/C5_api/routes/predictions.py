from fastapi import APIRouter, Depends, Body

from src.C5_api.utils.deps import get_current_user, get_db, require_role_script

router = APIRouter(prefix="/predictions", tags=["predictions"])


@router.get("/hourly_by_trading_pair_id/{trading_pair_id}")
def get_predictions_hourly(trading_pair_id: int, start_date: str = None, db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.prediction_hourly.get_predictions_by_trading_pair(trading_pair_id, start_date)


@router.get("/daily_by_trading_pair_id/{trading_pair_id}")
def get_predictions_daily(trading_pair_id: int, start_date: str = None, db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.prediction_daily.get_predictions_by_trading_pair(trading_pair_id, start_date)


@router.get("/last_hourly_by_trading_pair_id/{trading_pair_id}")
def get_last_prediction_hourly(trading_pair_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.prediction_hourly.get_last_prediction_by_trading_pair(trading_pair_id)


@router.get("/last_daily_by_trading_pair_id/{trading_pair_id}")
def get_last_prediction_daily(trading_pair_id: int, db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.prediction_daily.get_last_prediction_by_trading_pair(trading_pair_id)


@router.post("/hourly")
def create_prediction_hourly(payload: dict = Body(...), db=Depends(get_db), current_user=Depends(require_role_script)):
    obj = db.prediction_hourly.create(**payload)
    return obj


@router.post("/daily")
def create_prediction_daily(payload: dict = Body(...), db=Depends(get_db), current_user=Depends(require_role_script)):
    obj = db.prediction_daily.create(**payload)
    return obj
