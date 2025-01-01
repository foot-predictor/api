from datetime import date
from enum import Enum

from sqlalchemy import Column, String
from sqlmodel import Field, Relationship, SQLModel

from models.teams import Team

LEAGUE = "league"
CUP = "cup"


class CompetitionType(str, Enum):
    LEAGUE = "league"
    CUP = "cup"


class CompetitionTeamLink(SQLModel, table=True):
    team_id: int = Field(
        default=None, foreign_key="team.id", primary_key=True, ondelete="CASCADE"
    )
    competition_id: int = Field(
        default=None, foreign_key="competition.id", primary_key=True, ondelete="CASCADE"
    )


class Competition(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type_: CompetitionType = Field(sa_column=Column(String, nullable=False))
    name: str
    place_code: str
    place_name: str
    logo_url: str | None = None
    data_id: str = Field(unique=True)
    stats_id: int = Field(unique=True)
    start_date: date = Field(nullable=True, default=None)

    teams: list["Team"] = Relationship(
        back_populates="_competitions",
        link_model=CompetitionTeamLink,
    )

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)