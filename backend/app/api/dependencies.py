from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

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
    return session
