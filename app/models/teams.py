import math
from functools import cached_property

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


class TeamBaseStats(SQLModel):
    gf: int
    ga: int
    mp: int
    wins: int
    draws: int
    loses: int


class TeamSideStats(TeamBaseStats):
    nb_attacks: int
    nb_shots_total: int
    nb_shots_on_goal_total: int
    possession_avg: float
    passes_accuracy_avg: float

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def goal_per_match(self) -> float:
        return self.gf / self.mp

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def attack_efficiency(self) -> float:
        atk_for_goal_ratio = self.nb_attacks / self.gf
        atk_per_match = self.nb_attacks / self.mp
        atk_for_sog = self.nb_attacks / self.nb_shots_on_goal_total
        shot_on_goal_for_goal = self.nb_shots_on_goal_total / self.gf
        atk_for_goal = shot_on_goal_for_goal / atk_for_sog
        return atk_for_goal / atk_per_match * atk_for_goal_ratio

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shot_accuracy(self) -> float:
        shot_on_goal_ratio = self.nb_shots_on_goal_total / self.nb_shots_total
        shot_on_goal_for_goal = self.nb_shots_on_goal_total / self.gf
        shot_on_goal_per_match = self.nb_shots_on_goal_total / self.mp
        return shot_on_goal_for_goal / shot_on_goal_per_match * shot_on_goal_ratio

    @cached_property
    def _xg_per_attack(self) -> float:
        atk_for_goal = self.nb_attacks / self.gf
        atk_for_shot_on_goal = self.nb_attacks / self.nb_shots_on_goal_total
        return (
            self.nb_attacks
            * (
                (atk_for_goal + atk_for_shot_on_goal)
                / self.nb_attacks
                * self.attack_efficiency
            )
            / 100
        ) * 0.4

    @cached_property
    def _xg_per_shot(self) -> float:
        shot_per_match = self.nb_shots_total / self.mp
        shot_for_goal = self.nb_shots_on_goal_total / self.gf
        return (
            (
                self.nb_shots_total
                * (
                    (shot_per_match + shot_for_goal)
                    / self.nb_shots_total
                    * self.shot_accuracy
                )
            )
            / 100
        ) * 0.4

    @computed_field  # type: ignore[prop-decorator]
    @property
    def xg(self) -> float:
        possessions_weight = 1 + (self.possession_avg - 0.50)
        passes_accuracy_weight = 1 + (self.passes_accuracy_avg - 0.80)

        combined_xgs = (
            self._xg_per_attack * possessions_weight * passes_accuracy_weight
        ) / self._xg_per_shot

        return self.goal_per_match * (0.75 + math.log10(combined_xgs))


class TeamAllStats(TeamBaseStats):
    team: Team
    home: TeamSideStats
    away: TeamSideStats

    @computed_field  # type: ignore[prop-decorator]
    @property
    def xg(self) -> float:
        return (self.home.xg + self.away.xg) / 2


from models.matchs import MatchStatistics

Team.model_rebuild()
