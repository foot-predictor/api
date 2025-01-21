from core.dependencies import SessionDep
from fastapi import APIRouter
from models import Team

router = APIRouter()


@router.get("/")
def teams(session: SessionDep) -> list[Team]:
    return session.query(Team).all()
