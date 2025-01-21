from pydantic import computed_field
from sqlmodel import Field, Relationship, SQLModel

from models.competitions import Competition, CompetitionTeamLink, CompetitionType


class TeamBase(SQLModel):
    name: str
    short_name: str
    tag: str
    city: str
    venue_name: str
    logo_url: str
    data_id: int
    livescore_id: int
    transfermarkt_id: int


class TeamCreate(SQLModel):
    leagues: list[int]
    cups: list[int]


class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(unique=True)
    data_id: int = Field(unique=True)
    livescore_id: int = Field(unique=True, nullable=True)
    transfermarkt_id: int = Field(unique=True, nullable=True)

    # Defining relationships for leagues and cups
    _competitions: list[Competition] = Relationship(
        back_populates="teams",
        link_model=CompetitionTeamLink,
        sa_relationship_kwargs={
            "passive_deletes": True,
        },
    )
    matches: list["MatchStatistics"] = Relationship(back_populates="team")

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    @computed_field  # type: ignore[prop-decorator]
    @property
    def leagues(self) -> list[Competition]:
        return list(
            filter(lambda c: c.type_ == CompetitionType.LEAGUE, self._competitions)
        )

    @computed_field  # type: ignore[prop-decorator]
    @property
    def cups(self) -> list[Competition]:
        return list(
            filter(lambda c: c.type_ == CompetitionType.CUP, self._competitions)
        )

    def is_in_league(self, league: "Competition") -> bool:
        return any(competition.id == league.id for competition in self.leagues)

    def is_in_cup(self, cup: "Competition") -> bool:
        return any(competition.id == cup.id for competition in self.cups)


from models.matchs import MatchStatistics

Team.model_rebuild()
