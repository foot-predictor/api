from core.dependencies import SessionDep
from fastapi import APIRouter
from models import Competition, CompetitionType

router = APIRouter()


@router.get("/leagues")
def leagues(session: SessionDep) -> list[Competition]:
    return (
        session.query(Competition)
        .where(Competition.type_ == CompetitionType.LEAGUE.value)  # type: ignore
        .all()
    )


@router.get("/cups")
def cups(session: SessionDep) -> list[Competition]:
    return (
        session.query(Competition)
        .where(Competition.type_ == CompetitionType.LEAGUE.value)  # type: ignore
        .all()
    )


@router.post("/leagues")
def add_league(league: Competition, session: SessionDep) -> Competition:
    session.add(league)
    session.commit()
    session.refresh(league)
    return league


@router.post("/cups")
def add_cup(cup: Competition, session: SessionDep) -> Competition:
    session.add(cup)
    session.commit()
    session.refresh(cup)
    return cup
