from fastapi import APIRouter, HTTPException

from core.dependencies import SessionDep
from models import Team, TeamCreate, TeamUpdate

router = APIRouter()


@router.get("/")
def teams(session: SessionDep) -> list[Team]:
    return session.query(Team).all()


@router.post("/")
def create_team(team: TeamCreate, session: SessionDep) -> Team:
    obj = Team.model_validate(team)
    session.add(obj)
    session.commit()
    session.refresh(obj)
    return obj


@router.get("/{team_id}")
def get_team(team_id: int, session: SessionDep) -> Team:
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team ({team_id}) not found.")

    return team


@router.patch("/{team_id}")
def update_team(team_id: int, team_updated: TeamUpdate, session: SessionDep) -> Team:
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail=f"Team ({team_id}) not found.")

    team.sqlmodel_update(team_updated.model_dump(exclude_unset=True))
    session.add(team)
    session.commit()
    session.refresh(team)
    return team
