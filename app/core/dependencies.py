from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, FastAPI, Request
from sqlmodel import Session

from core.db import engine


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]


def get_current_app(request: Request) -> Generator:
    yield request.app


CurrentAppDep = Annotated[FastAPI, Depends(get_current_app)]
