from fastapi import APIRouter, Depends, Header, HTTPException, status

from app.api.dependencies import get_current_session
from app.config import get_settings
from app.schemas.auth import LoginRequest, LoginResponse, MeResponse
from app.services.session_store import session_store

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest):
    settings = get_settings()
    if (
        payload.username.strip() != settings.admin_username
        or payload.password != settings.admin_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号或密码错误",
        )

    session = session_store.create(settings.admin_username)
    return LoginResponse(token=session.token, username=session.username)


@router.post("/logout")
def logout(authorization: str | None = Header(default=None)):
    token = (authorization or "").removeprefix("Bearer ").strip()
    session_store.delete(token)
    return {"ok": True}


@router.get("/me", response_model=MeResponse)
def me(session=Depends(get_current_session)):
    return MeResponse(logged_in=True, username=session.username)
