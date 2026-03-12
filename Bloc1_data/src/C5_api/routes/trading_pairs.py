from fastapi import APIRouter, Depends

from src.C5_api.utils.deps import get_current_user, get_db

router = APIRouter(
    prefix="/trading_pairs",
    tags=["trading_pairs"]
)


@router.get("/trading_pairs_by_base_currency_symbol/{symbol}")
def get_trading_pairs_by_base_currency_symbol(symbol: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    trading_pairs = db.trading_pairs.get_pairs_by_base_currency_symbol(symbol.upper())
    return trading_pairs


@router.get("/trading_pair_by_currency_symbols/{base_symbol}/{quote_symbol}")
def get_trading_pair_by_currency_symbols(base_symbol: str, quote_symbol: str, db=Depends(get_db), current_user=Depends(get_current_user)):
    trading_pair = db.trading_pairs.get_pair_by_currency_symbols(base_symbol.upper(), quote_symbol.upper())
    return trading_pair
