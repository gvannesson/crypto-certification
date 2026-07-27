from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt

from src.settings import SecretSettings

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(password: str) -> bool:
    return password == SecretSettings.E3_PASSWORD


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SecretSettings.E3_SECRET_KEY, algorithm=SecretSettings.E3_ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SecretSettings.E3_SECRET_KEY, algorithms=[SecretSettings.E3_ALGORITHM])
        return payload
    except JWTError:
        return None
