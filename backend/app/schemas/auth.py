from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=80)
    password: str = Field(..., min_length=6, max_length=128)


class LoginResponse(BaseModel):
    ok: bool = True
    token: str
    username: str


class MeResponse(BaseModel):
    logged_in: bool
    username: str = ""
