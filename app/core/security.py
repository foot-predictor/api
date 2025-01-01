import bcrypt
from sqlmodel import SQLModel


class Password(SQLModel):
    password: str


def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed)
