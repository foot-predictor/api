import base64
import os
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import delete, text
from sqlalchemy.exc import OperationalError
from sqlmodel import select

from alembic.config import Config
from alembic.script import ScriptDirectory
from core.dependencies import CurrentAppDep, SessionDep
from core.security import Password, verify_password
from models import Competition, CompetitionType, Team

router = APIRouter()


@router.get("/healthcheck")
def healthcheck(session: SessionDep, current_app: CurrentAppDep) -> dict[str, str]:
    try:
        revisions = session.exec(text("SELECT version_num FROM alembic_version")).all()  # type: ignore
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


@router.post("/initialize")
def initialize(
    password: Password,
    session: SessionDep,
    current_app: CurrentAppDep,
    force_clean: Annotated[bool, Query()] = False,
) -> dict[str, str]:
    if not verify_password(
        password.password, base64.b64decode(current_app.state.config.ADMIN_PASSWORD)
    ):
        raise HTTPException(
            status_code=401,
            detail={"status": "UNAUTHORIZED", "message": "Invalid credentials."},
        )

    if (
        session.exec(select(Competition).limit(1)).first() is not None  # type: ignore
        or session.exec(select(Competition).limit(1)).first() is not None  # type: ignore
    ) and not force_clean:
        return {
            "status": "NOTHING_DONE",
            "message": "Database is already initialized.",
        }

    if force_clean:
        session.exec(delete(Competition))  # type: ignore
        session.exec(delete(Team))  # type: ignore

    league_df = pd.read_json("initial_data/leagues.json")
    teams_df = pd.read_json("initial_data/teams.json")

    leagues = {}
    for league in league_df.to_dict(orient="records"):  # call-overload: ignore
        type_league = CompetitionType(league.pop("type_"))
        leagues[league["data_id"]] = Competition(type_=type_league, **league)  # type: ignore

    teams = [
        {**data, "_competitions": [leagues[data_id] for data_id in data.pop("leagues")]}
        for data in teams_df.to_dict(orient="records")
    ]

    session.add_all([Team(**team) for team in teams])  # type: ignore
    session.commit()

    return {
        "status": "OK",
        "message": "Database is successfully initialized.",
    }
