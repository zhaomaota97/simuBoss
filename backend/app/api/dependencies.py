from datetime import datetime, timedelta

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db
from app.models import SessionToken


def get_current_session(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    token = (authorization or "").removeprefix("Bearer ").strip()
    session = db.get(SessionToken, token) if token else None
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已失效",
        )

    expires_at = session.created_at + timedelta(hours=get_settings().session_ttl_hours)
    if datetime.utcnow() >= expires_at:
        db.delete(session)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="登录已过期，请重新登录",
        )

    return session
