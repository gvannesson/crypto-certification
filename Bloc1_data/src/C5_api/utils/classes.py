from pydantic import BaseModel
from datetime import datetime


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegister(BaseModel):
    username: str
    password: str


class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str


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


class PredictionUpdate(BaseModel):
    predicted_class: int | None = None
    predicted_label: str | None = None
    confidence: float | None = None
    model_name: str | None = None
