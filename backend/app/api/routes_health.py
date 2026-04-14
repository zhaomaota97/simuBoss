from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check():
    settings = get_settings()
    return {
        "ok": True,
        "service": settings.app_name,
        "env": settings.app_env,
    }
