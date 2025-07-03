# app/schemas/msg.py
from pydantic import BaseModel


class Msg(BaseModel):
    msg: str
