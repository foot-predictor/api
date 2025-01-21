import datetime
import enum

from sqlalchemy import Column, Enum
from sqlmodel import Field, Relationship, SQLModel

from models.teams import Team


class MatchStatus(enum.IntEnum):
    NO_DATA = 0
    NOT_STARTED = 1
    FINISHED = 2


class MatchSide(enum.IntEnum):
    HOME = 1
    AWAY = 2


class MatchResult(enum.IntEnum):
    LOSE = 0
    DRAW = 1
    WIN = 2


class MatchStatistics(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.id", ondelete="CASCADE")
    data_id: int | None
    livescore_id: int | None
    transfermarkt_id: int | None
    date: datetime.datetime

    status: MatchStatus = Field(
        sa_column=Column(Enum(MatchStatus)), default=MatchStatus.NO_DATA
    )
    side: MatchSide | None = Field(
        sa_column=Column(Enum(MatchSide), nullable=True), default=None
    )
    result: MatchResult | None = Field(
        sa_column=Column(Enum(MatchResult), nullable=True), default=None
    )

    goal_for: int | None
    goal_against: int | None
    fouls: int | None
    shots: int | None
    shots_off_goal: int | None
    shots_on_goal: int | None
    possession: int | None

    livescore_xg: float | None

    # relationships
    team: Team = Relationship(back_populates="matches")
