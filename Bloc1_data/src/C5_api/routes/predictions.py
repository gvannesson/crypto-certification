from fastapi import APIRouter, Depends, Body, HTTPException, status

from src.C5_api.utils.classes import PredictionUpdate
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


@router.put("/hourly/{prediction_id}")
def update_prediction_hourly(
    prediction_id: int,
    payload: PredictionUpdate,
    db=Depends(get_db),
    current_user=Depends(require_role_script),
):
    existing = db.prediction_hourly.get(prediction_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    updated_fields = payload.model_dump(exclude_none=True)
    if not updated_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    return db.prediction_hourly.update(prediction_id, **updated_fields)


@router.put("/daily/{prediction_id}")
def update_prediction_daily(
    prediction_id: int,
    payload: PredictionUpdate,
    db=Depends(get_db),
    current_user=Depends(require_role_script),
):
    existing = db.prediction_daily.get(prediction_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    updated_fields = payload.model_dump(exclude_none=True)
    if not updated_fields:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No fields to update")
    return db.prediction_daily.update(prediction_id, **updated_fields)


@router.delete("/hourly/{prediction_id}")
def delete_prediction_hourly(
    prediction_id: int,
    db=Depends(get_db),
    current_user=Depends(require_role_script),
):
    existing = db.prediction_hourly.get(prediction_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    db.prediction_hourly.delete(prediction_id)
    return {"message": f"Prediction {prediction_id} deleted successfully"}


@router.delete("/daily/{prediction_id}")
def delete_prediction_daily(
    prediction_id: int,
    db=Depends(get_db),
    current_user=Depends(require_role_script),
):
    existing = db.prediction_daily.get(prediction_id)
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Prediction not found")
    db.prediction_daily.delete(prediction_id)
    return {"message": f"Prediction {prediction_id} deleted successfully"}
