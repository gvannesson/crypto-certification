from pydantic import BaseModel
from datetime import datetime


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class PredictionCreate(BaseModel):
    trading_pair_id: int
    date: datetime
    predicted_class: int
    predicted_label: str
    confidence: float | None = None
    model_name: str | None = None
