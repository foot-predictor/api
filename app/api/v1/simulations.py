import pandas as pd
from fastapi import APIRouter, HTTPException

from core.dependencies import CurrentAppDep, SessionDep
from libs.football_data_api.service import FootballDataApiService
from libs.football_stats_api import FootballStatsApiService
from libs.predictor import Predictor, PredictorError
from models import MatchIN, MatchPredictions, Team

router = APIRouter()


@router.post("/")
def simulate(
    match: MatchIN, session: SessionDep, current_app: CurrentAppDep
) -> MatchPredictions:
    home_team = session.get(Team, match.home_team)
    away_team = session.get(Team, match.away_team)

    if home_team is None or away_team is None:
        raise HTTPException(
            status_code=404,
            detail={
                "status": "NOT_FOUND",
                "message": f"Team {match.home_team if match.home_team is None else match.away_team} not found.",
            },
        )

    common_leagues = set(home_team.leagues) & set(away_team.leagues)
    common_cups = set(home_team.cups) & set(away_team.cups)
    if not common_leagues and not common_cups:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "MATCH_NOT_POSSIBLE",
                "message": "Both teams haven't got 1 league or cup in common.",
            },
        )

    data_api_service = FootballDataApiService(
        current_app.state.config.FOOTBALL_DATA_API_KEY
    )
    stats_api_service = FootballStatsApiService(
        current_app.state.config.FOOTBALL_STATS_API_KEY
    )

    start_date = min(
        [
            *[league.start_date for league in common_leagues],
            *[league.start_date for league in common_leagues],
        ]
    )
    home_matches, home_team_result = data_api_service.get_team_matches(
        home_team.data_id, season=start_date.year
    )
    away_matches, away_team_result = data_api_service.get_team_matches(
        away_team.data_id, season=start_date.year
    )
    home_stats = stats_api_service.get_team_matches_statistics(
        home_team.stats_id,
        start_date,
    )
    away_stats = stats_api_service.get_team_matches_statistics(
        away_team.stats_id,
        start_date,
    )

    home_matches = pd.merge(
        home_matches,
        home_stats,
        left_on="matchday",
        right_on="match_round",
        how="inner",
    )
    away_matches = pd.merge(
        away_matches,
        away_stats,
        left_on="matchday",
        right_on="match_round",
        how="inner",
    )

    predictor = Predictor(home_team=home_team, away_team=away_team)
    predictor.enhance_team_statistics(home_matches, away_matches)

    try:
        return predictor.simulate()
    except PredictorError as e:
        raise HTTPException(
            status_code=500,
            detail={"status": "PREDICTION_ERROR", "message": str(e)},
        )
