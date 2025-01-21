from collections.abc import Generator

from fastapi import Request
from sqlmodel import Session

from core.db import engine


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


def get_current_app(request: Request) -> Generator:
    yield request.app
