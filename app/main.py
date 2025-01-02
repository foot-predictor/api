from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from logging.config import dictConfig

import yaml
from fastapi import FastAPI

from api import main, v1
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    app.state.config = settings

    # INCLUDE ROUTERS
    app.include_router(main.router, tags=["Utilities"])
    app.include_router(v1.router, prefix="/api/v1")

    # SETUP LOGGING
    with open("logging.yaml") as stream:
        logging_config = yaml.safe_load(stream)
        dictConfig(logging_config)

    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    debug=settings.DEBUG,
    version=settings.VERSION,
    lifespan=lifespan,
)
