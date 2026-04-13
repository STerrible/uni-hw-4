from hashlib import sha256

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User
from app.schemas import LoginRequest, UserAuthOut, UserCreate

router = APIRouter(prefix="/auth", tags=["auth"])

active_sessions: set[int] = set()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def hash_password(password: str) -> str:
    return sha256(password.encode("utf-8")).hexdigest()


def get_current_user(x_user_id: int = Header(..., alias="X-User-Id"), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == x_user_id).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не найден")
    if user.id not in active_sessions:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Пользователь не авторизован")
    return user


@router.post("/register", response_model=UserAuthOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Пользователь уже существует")

    user = User(username=payload.username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserAuthOut(user_id=user.id, username=user.username)


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or user.password_hash != hash_password(payload.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверные учетные данные")

    active_sessions.add(user.id)
    return {
        "message": "Успешный вход",
        "user_id": user.id,
        "auth_type": "identifier",
        "use_header": {"X-User-Id": user.id},
    }


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    active_sessions.discard(current_user.id)
    return {"message": "Сессия завершена", "user_id": current_user.id}
