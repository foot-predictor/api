from pydantic import computed_field
from sqlmodel import Field, Relationship, SQLModel

from models import Competition
from models.competitions import CompetitionTeamLink, CompetitionType


class TeamBase(SQLModel):
    name: str
    short_name: str
    tag: str
    city: str
    venue_name: str
    logo_url: str
    data_id: int
    stats_id: int


class TeamCreate(SQLModel):
    leagues: list[int]
    cups: list[int]


class TeamUpdate(SQLModel):
    name: str | None = None
    short_name: str | None = None
    tag: str | None = None
    city: str | None = None
    venue_name: str | None = None
    logo_url: str | None = None
    data_id: int | None = None
    stats_id: int | None = None
    leagues: list[int] | None = None
    cups: list[int] | None = None


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    data_id: int = Field(unique=True)
    stats_id: int = Field(unique=True)

    # Defining relationships for leagues and cups
    _competitions: list[Competition] = Relationship(
        back_populates="teams",
        link_model=CompetitionTeamLink,
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @computed_field
    def leagues(self) -> list[Competition]:
        return list(
            filter(lambda c: c.type_ == CompetitionType.LEAGUE, self._competitions)
        )

    @computed_field
    def cups(self) -> list[Competition]:
        return list(
            filter(lambda c: c.type_ == CompetitionType.CUP, self._competitions)
        )

    def is_in_league(self, league: "Competition") -> bool:
        return any(competition.id == league.id for competition in self.leagues)

    def is_in_cup(self, cup: "Competition") -> bool:
        return any(competition.id == cup.id for competition in self.cups)
