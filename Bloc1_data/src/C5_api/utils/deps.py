from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from src.C4_database.database import Database
from src.C5_api.utils.auth import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/authentification/login")


def get_db():
    try:
        with Database() as db:
            yield db
    finally:
        db.session.close()


def get_current_user(token: str = Depends(oauth2_scheme), db: Database = Depends(get_db)):
    payload = decode_access_token(token)
    if payload is None or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.users.get_by_username(payload["sub"])
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return user


def require_role_script(current_user=Depends(get_current_user)):
    if getattr(current_user, "role", None) != "script":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted: script role required",
        )
    return current_user
