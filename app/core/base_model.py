from typing import Literal

from sqlmodel import SQLModel


class ServerStatus(SQLModel):
    status: Literal["OK", "ERROR"]


class ActionMessage(SQLModel):
    status: Literal["OK", "ERROR", "NOTHING_DONE"]
    message: str
