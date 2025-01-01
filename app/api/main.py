import os

from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from alembic.config import Config
from alembic.script import ScriptDirectory
from core.dependencies import CurrentAppDep, SessionDep

router = APIRouter()


@router.get("/healthcheck")
def healthcheck(session: SessionDep, current_app: CurrentAppDep) -> dict[str, str]:
    try:
        revisions = session.exec(text("SELECT version_num FROM alembic_version")).all()
    except OperationalError:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "DATABASE_CONNECTION_ERROR",
                "message": "Could not connect to database",
            },
        )

    alembic_cfg_path = os.path.join(current_app.state.config.BASE_DIR, "alembic.ini")
    alembic_cfg = Config(alembic_cfg_path)
    script = ScriptDirectory.from_config(alembic_cfg)

    if any(
        head for head in script.get_heads() if head not in [r for (r,) in revisions]
    ):
        raise HTTPException(
            status_code=500,
            detail={
                "error": "DATABASE_MIGRATION_ERROR",
                "message": "Database is not up-to-date",
            },
        )

    return {"status": "OK"}
