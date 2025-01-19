import datetime
import enum

from sqlalchemy import Column, Enum
from sqlmodel import Field, Relationship, SQLModel

from models.teams import Team


class MatchStatus(enum.IntEnum):
    NOT_STARTED = 0
    FINISHED = 1


class MatchStatistics(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.id", ondelete="CASCADE")
    data_id: int | None
    livescore_id: int | None
    transfermarkt_id: int | None
    status: MatchStatus = Field(
        sa_column=Column(Enum(MatchStatus)), default=MatchStatus.NOT_STARTED
    )
    date: datetime.datetime

    goal_for: int | None
    goal_against: int | None
    fouls: int | None
    shots: int | None
    shots_off_goal: int | None
    shots_on_goal: int | None
    attacks: int | None
    possession: int | None

    livescore_xg: float | None

    # relationships
    team: Team = Relationship(back_populates="matches")
