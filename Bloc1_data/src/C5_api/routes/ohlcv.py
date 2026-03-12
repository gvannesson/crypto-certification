from fastapi import APIRouter, Depends

from src.C5_api.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/ohlcv", tags=["ohlcv"])


@router.get("/minute_by_trading_pair_id/{trading_pair_id}")
def get_ohlcv_minute(trading_pair_id: int, start_date: str = None, db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.ohlcv_minute.get_ohlcv_by_trading_pair(trading_pair_id, start_date)


@router.get("/hourly_by_trading_pair_id/{trading_pair_id}")
def get_ohlcv_hourly(trading_pair_id: int, start_date: str = None, db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.ohlcv_hourly.get_ohlcv_by_trading_pair(trading_pair_id, start_date)


@router.get("/daily_by_trading_pair_id/{trading_pair_id}")
def get_ohlcv_daily(trading_pair_id: int, start_date: str = None, db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.ohlcv_daily.get_ohlcv_by_trading_pair(trading_pair_id, start_date)
