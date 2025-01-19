from sqlmodel import SQLModel

from models.teams import TeamAllStats


class PredictionIN(SQLModel):
    home_team: int
    away_team: int


class ThresholdGoal(SQLModel):
    threshold: float
    below: int
    over: int


class Predictions(SQLModel):
    home_team: TeamAllStats
    away_team: TeamAllStats

    home_win: int = 0
    draw: int = 0
    away_win: int = 0
    btts: int = 0
    global_threshold_goals: list[ThresholdGoal] = []
    home_threshold_goals: list[ThresholdGoal] = []
    away_threshold_goals: list[ThresholdGoal] = []
    exact_score: list[dict[str, int]] = []
