from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from src.settings import SecretSettings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password):
    return pwd_context.hash(password)


get_password_hash = hash_password


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SecretSettings.API_SECRET_KEY, algorithm=SecretSettings.API_ALGORITHM)


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SecretSettings.API_SECRET_KEY, algorithms=[SecretSettings.API_ALGORITHM])
        return payload
    except JWTError:
        return None
