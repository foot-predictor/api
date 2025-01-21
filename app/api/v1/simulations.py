import logging

import pandas as pd
from fastapi import APIRouter, HTTPException

from core.dependencies import MatchExtractorDep, SessionDep
from models import PredictionIN, ResultPredictions, Team
from predictor import Predictor, PredictorError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/")
def simulate(
    match: PredictionIN, session: SessionDep, matches_extractor: MatchExtractorDep
) -> ResultPredictions:
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
    try:
        predictor = Predictor(home_team=home_team, away_team=away_team)
    except AssertionError:
        raise HTTPException(
            status_code=400,
            detail={
                "status": "MATCH_IMPOSSIBLE",
                "message": "The 2 teams are not in a common league or cup.",
            },
        )
    logger.info("Extract team matches")
    home_matches, away_matches = matches_extractor.get_match_data(
        home_team=home_team,
        away_team=away_team,
        season=min(comp.start_date.year for comp in predictor.common_competitions),
    )
    if home_matches:
        logger.info(
            f"Update [{len(home_matches)}] matches for team [{home_team.short_name}]"
        )
        session.add_all(home_matches)
    if away_matches:
        logger.info(
            f"Update [{len(home_matches)}] matches for team [{home_team.short_name}]"
        )
        session.add_all(home_matches)
    session.commit()
    for m in home_matches + away_matches:
        session.refresh(m)

    logger.info("Aggregate matches statistics")
    predictor.enhance_team_statistics(
        pd.DataFrame([m.model_dump(mode="json") for m in home_matches]),
        pd.DataFrame([m.model_dump(mode="json") for m in away_matches]),
    )

    try:
        prediction = predictor.simulate()
        return ResultPredictions(
            home_team=home_team,
            away_team=away_team,
            home_stats=predictor.home_stats,
            away_stats=predictor.away_stats,
            prediction=prediction,
        )
    except PredictorError as e:
        logger.error(f"Error during prediction: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail={"status": "PREDICTION_ERROR", "message": str(e)},
        )
