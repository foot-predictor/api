import base64
import logging
import os
from typing import Annotated

import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import delete, text
from sqlalchemy.exc import OperationalError
from sqlmodel import select

from alembic.config import Config
from alembic.script import ScriptDirectory
from core.base_model import ActionMessage, ServerStatus
from core.dependencies import CurrentAppDep, SessionDep
from core.security import Password, verify_password
from models import Competition, CompetitionType, MatchStatistics, Team

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/healthcheck")
def healthcheck(session: SessionDep, current_app: CurrentAppDep) -> ServerStatus:
    try:
        logger.info("Getting database revisions, to check database is available")
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
    migrations = script.get_heads()

    logger.info("Compare database revisions with latest available migrations")
    if any(head for head in migrations if head not in [r for (r,) in revisions]):
        logger.info(f"Database is not up-to-date, missing one of {migrations}")
        raise HTTPException(
            status_code=500,
            detail={
                "error": "DATABASE_MIGRATION_ERROR",
                "message": "Database is not up-to-date",
            },
        )

    return ServerStatus(status="OK")


@router.post("/initialize")
def initialize(
    password: Password,
    session: SessionDep,
    current_app: CurrentAppDep,
    force_clean: Annotated[bool, Query()] = False,
) -> ActionMessage:
    logger.info("Verifying admin password")
    if not verify_password(
        password.password, base64.b64decode(current_app.state.config.ADMIN_PASSWORD)
    ):
        logger.info("Invalid admin password")
        raise HTTPException(
            status_code=401,
            detail={"status": "UNAUTHORIZED", "message": "Invalid credentials."},
        )

    logger.info("Verify if data already exists and if force_clean is True")
    if (
        session.exec(select(Competition).limit(1)).first() is not None  # type: ignore
        or session.exec(select(Competition).limit(1)).first() is not None  # type: ignore
    ) and not force_clean:
        return ActionMessage(
            status="NOTHING_DONE",
            message="Database is already initialized.",
        )

    if force_clean:
        logger.info("Force cleaning database")
        session.exec(delete(Competition))  # type: ignore
        session.exec(delete(Team))  # type: ignore

    league_df = pd.read_json("initial_data/leagues.json")
    teams_df = pd.read_json("initial_data/teams.json")

    leagues = {}
    for league in league_df.to_dict(orient="records"):  # call-overload: ignore
        type_league = CompetitionType(league.pop("type_"))
        leagues[league["data_id"]] = Competition(type_=type_league, **league)  # type: ignore

    logger.info(f"Adding {len(leagues)} leagues.")
    teams = []
    matches = []
    for data in teams_df.to_dict(orient="records"):
        leagues_id = data.pop("leagues")
        match_list = data.pop("matchs")
        team = Team(**data)
        team._competitions = [leagues[league_id] for league_id in leagues_id]

        teams.append(team)
        matches.extend(
            [MatchStatistics(team=team, **match_data) for match_data in match_list]
        )

    logger.info(f"Adding {len(teams)} teams.")
    session.add_all(teams)  # type: ignore
    logger.info(f"Adding {len(matches)} matches.")
    session.add_all(matches)  # type: ignore
    session.commit()

    return ActionMessage(
        status="OK",
        message="Database is successfully initialized.",
    )
