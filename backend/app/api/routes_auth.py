from uuid import uuid4

from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_session
from app.config import get_settings
from app.db import get_db
from app.models import SessionToken, User
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse, RegisterRequest
from app.services.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    settings = get_settings()
    username = payload.username.strip()
    user = db.query(User).filter(User.username == username).first()

    if not user and username == settings.admin_username and payload.password == settings.admin_password:
        user = User(username=username, password_hash=hash_password(payload.password))
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )

    token = uuid4().hex
    db.add(SessionToken(token=token, user_id=user.id, username=user.username))
    db.commit()
    return LoginResponse(token=token, username=user.username)


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    username = payload.username.strip()
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="账号已存在")

    user = User(username=username, password_hash=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = uuid4().hex
    db.add(SessionToken(token=token, user_id=user.id, username=user.username))
    db.commit()
    return LoginResponse(token=token, username=user.username)


@router.post("/logout")
def logout(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    token = (authorization or "").removeprefix("Bearer ").strip()
    if token:
        session = db.get(SessionToken, token)
        if session:
            db.delete(session)
            db.commit()
    return {"ok": True}


@router.get("/me", response_model=MeResponse)
def me(session=Depends(get_current_session)):
    return MeResponse(logged_in=True, username=session.username)
