from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from src.C5_api.utils.auth import verify_password, create_access_token, get_password_hash
from src.C5_api.utils.classes import UserRegister
from src.C4_database.database import Database
from src.C5_api.utils.deps import get_db


router = APIRouter(
    prefix="/authentification",
    tags=["authentification"]
)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Database = Depends(get_db)):
    user = db.users.get_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user.role
    }


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Database = Depends(get_db)):
    existing_user = db.users.get_by_username(payload.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    hashed_password = get_password_hash(payload.password)
    user = db.users.create(
        username=payload.username,
        password_hashed=hashed_password,
        role="user"
    )
    return {"id": user.id, "username": user.username, "role": user.role}
