import math
from functools import cached_property

from pydantic import computed_field
from sqlmodel import SQLModel


class TeamStatistics(SQLModel):
    matches_played: int
    wins: int
    draws: int
    losses: int
    goals_for: int
    goals_against: int
    fouls: int
    shots: int
    shots_off_goal: int
    shots_on_goal: int
    possession: float
    external_xg: float | None = None

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def goal_per_match(self) -> float:
        return self.goals_for / self.matches_played

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shot_per_match(self) -> float:
        return self.shots / self.matches_played

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shots_on_goal_per_match(self) -> float:
        return self.shots_on_goal / self.matches_played

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shots_on_goal_for_goal(self) -> float:
        return self.shots_on_goal / self.goals_for

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shot_accuracy(self) -> float:
        return self.shots_on_goal / self.shots

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shot_quality(self) -> float:
        return self.goals_for / self.shots_on_goal

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def attack_efficiency_ratio(self) -> float:
        return (self.goals_for * self.goal_per_match) / 100

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def probability_of_goal_per_shot(self) -> float:
        return (
            (self.shot_per_match * self.shot_quality)
            / (self.shots_on_goal_for_goal * self.shot_accuracy)
        ) / 100

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def xg(self) -> float:
        xg_per_shot = (
            self.shots_on_goal * self.probability_of_goal_per_shot
        ) / self.matches_played

        possession_weight = 1 + (self.possession - 0.5)
        shot_accuracy_weight = 1 + (self.shot_accuracy - 0.3)

        probability_of_multiple_goal = (
            (self.shots_on_goal_per_match * self.shots_on_goal_for_goal)
            * (self.goal_per_match - 1)
            / 100
        )

        xg = math.exp2(
            xg_per_shot * shot_accuracy_weight
            + self.attack_efficiency_ratio * possession_weight
        ) * (1 + probability_of_multiple_goal)

        if self.external_xg is not None:
            xg = (xg * (1 - math.log(xg))) + (self.external_xg * math.log(xg))
        else:
            xg = (xg * (1 - math.log(xg))) + (1.3 * math.log(xg))
        return round(xg, 2)


class GlobalStatistics(SQLModel):
    home_statistics: TeamStatistics
    away_statistics: TeamStatistics

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def matches_played(self) -> int:
        return self.home_statistics.matches_played + self.away_statistics.matches_played

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def wins(self) -> int:
        return self.home_statistics.wins + self.away_statistics.wins

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def draws(self) -> int:
        return self.home_statistics.draws + self.away_statistics.draws

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def losses(self) -> int:
        return self.home_statistics.losses + self.away_statistics.losses

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def goals_for(self) -> int:
        return self.home_statistics.goals_for + self.away_statistics.goals_for

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def goals_against(self) -> int:
        return self.home_statistics.goals_against + self.away_statistics.goals_against

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def fouls(self) -> int:
        return self.home_statistics.fouls + self.away_statistics.fouls

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shots(self) -> int:
        return self.home_statistics.shots + self.away_statistics.shots

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shots_off_goal(self) -> int:
        return self.home_statistics.shots_off_goal + self.away_statistics.shots_off_goal

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def shots_on_goal(self) -> int:
        return self.home_statistics.shots_on_goal + self.away_statistics.shots_on_goal

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def possession(self) -> float:
        return self.home_statistics.possession + self.away_statistics.possession

    @computed_field  # type: ignore[prop-decorator]
    @cached_property
    def xg(self) -> float:
        return (self.home_statistics.xg + self.away_statistics.xg) / 2


class ThresholdGoal(SQLModel):
    threshold: float
    below: int
    over: int


class ExactScore(SQLModel):
    score: str
    probability: int


class Prediction(SQLModel):
    home_win: int = 0
    draw: int = 0
    away_win: int = 0
    btts: int = 0
    global_threshold_goals: list[ThresholdGoal] = []
    home_threshold_goals: list[ThresholdGoal] = []
    away_threshold_goals: list[ThresholdGoal] = []
    exact_score: list[ExactScore] = []
