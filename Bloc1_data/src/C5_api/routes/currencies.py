from fastapi import APIRouter, Depends

from src.C5_api.utils.deps import get_current_user, get_db

router = APIRouter(
    prefix="/currencies",
    tags=["currencies"]
)


@router.get("/all")
def get_all_currencies(db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.currencies.list_all()
