from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    ok: bool = True
    token: str
    username: str


class MeResponse(BaseModel):
    logged_in: bool
    username: str = ""
