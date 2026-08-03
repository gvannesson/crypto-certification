from pydantic import BaseModel


class ClassifyRequest(BaseModel):
    trading_pair_symbol: str
