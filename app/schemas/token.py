# app/schemas/token.py
from pydantic import BaseModel


class Token(BaseModel):
    uid: str
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
