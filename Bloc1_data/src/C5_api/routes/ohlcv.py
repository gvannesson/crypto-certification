from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query

from src.C5_api.utils.deps import get_current_user, get_db

router = APIRouter(prefix="/ohlcv", tags=["ohlcv"])


def _validate_start_date(start_date: str | None) -> str | None:
    """Valide le format YYYY-MM-DD si fourni, sinon renvoie HTTP 422."""
    if start_date is None:
        return None
    try:
        datetime.strptime(start_date, "%Y-%m-%d")
        return start_date
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail=f"Format de date invalide : '{start_date}'. Utiliser YYYY-MM-DD.",
        )


@router.get("/hourly_by_trading_pair_id")
def get_ohlcv_hourly(
    trading_pair_id: int,
    start_date: str = Query(None, description="Date de début au format YYYY-MM-DD"),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    validated = _validate_start_date(start_date)
    return db.ohlcv_hourly.get_ohlcv_by_trading_pair(trading_pair_id, validated)


@router.get("/daily_by_trading_pair_id")
def get_ohlcv_daily(
    trading_pair_id: int,
    start_date: str = Query(None, description="Date de début au format YYYY-MM-DD"),
    db=Depends(get_db),
    current_user=Depends(get_current_user),
):
    validated = _validate_start_date(start_date)
    return db.ohlcv_daily.get_ohlcv_by_trading_pair(trading_pair_id, validated)
