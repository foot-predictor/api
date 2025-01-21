from sqlmodel import SQLModel

from models.teams import Team
from predictor.models import GlobalStatistics, Prediction


class PredictionIN(SQLModel):
    home_team: int
    away_team: int


class ResultPredictions(SQLModel):
    home_team: Team
    away_team: Team
    home_stats: GlobalStatistics
    away_stats: GlobalStatistics
    prediction: Prediction
