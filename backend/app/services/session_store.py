from dataclasses import dataclass
from datetime import datetime
from threading import Lock
from uuid import uuid4


@dataclass
class Session:
    token: str
    username: str
    created_at: datetime


class SessionStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._sessions: dict[str, Session] = {}

    def create(self, username: str) -> Session:
        session = Session(token=uuid4().hex, username=username, created_at=datetime.utcnow())
        with self._lock:
            self._sessions[session.token] = session
        return session

    def get(self, token: str | None) -> Session | None:
        if not token:
            return None
        with self._lock:
            return self._sessions.get(token)

    def delete(self, token: str | None) -> None:
        if not token:
            return
        with self._lock:
            self._sessions.pop(token, None)


session_store = SessionStore()
