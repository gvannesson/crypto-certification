from fastapi import APIRouter, Depends

from src.C5_api.utils.deps import get_current_user, get_db

router = APIRouter(
    prefix="/exchanges",
    tags=["exchanges"]
)


@router.get("/all")
def get_all_exchanges(db=Depends(get_db), current_user=Depends(get_current_user)):
    return db.exchanges.list_all()
