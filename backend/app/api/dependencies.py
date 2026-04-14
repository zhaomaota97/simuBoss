from fastapi import Header, HTTPException, status

from app.services.session_store import session_store


def get_current_session(authorization: str | None = Header(default=None)):
    token = (authorization or "").removeprefix("Bearer ").strip()
    session = session_store.get(token)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未登录或登录已失效",
        )
    return session
