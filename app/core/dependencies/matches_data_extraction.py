import logging
import time
from datetime import datetime, timedelta
from typing import Annotated

import pandas as pd
from fastapi import Depends, FastAPI
from libs.football_data_api import FootballDataApiService
from libs.livescore_api import LiveScoreApiService
from models import MatchResult, MatchSide, MatchStatistics, MatchStatus, Team

from core.dependencies.base import get_current_app

logger = logging.getLogger(__name__)


class MatchesDataExtractor:
    def __init__(self, current_app: Annotated[FastAPI, Depends(get_current_app)]):
        self.data_api = FootballDataApiService(
            api_key=current_app.state.config.FOOTBALL_DATA_API_KEY,
        )
        self.livescore_api = LiveScoreApiService(
            api_key=current_app.state.config.RAPIDAPI_KEY,
            host=current_app.state.config.LIVESCORE_API_HOST,
            api_keys_spare=[
                current_app.state.config.RAPIDAPI_KEY_2,
                current_app.state.config.RAPIDAPI_KEY_3,
            ],
        )

    @staticmethod
    def _enrichment_match_statistics(
        match: MatchStatistics,
        data_match: pd.Series,
        livescore_match: list[dict[str, int]],
    ) -> MatchStatistics:
        match.status = (
            MatchStatus.FINISHED
            if data_match["status"] == "FINISHED"
            else MatchStatus.NOT_STARTED
        )
        match.side = (
            MatchSide.HOME
            if data_match["homeTeam.id"] == match.team.data_id
            else MatchSide.AWAY
        )
        match.result = (
            MatchResult.WIN
            if data_match["score.winner"] == f"{match.side.name}_TEAM"
            else MatchResult.DRAW
            if data_match["score.winner"] == MatchResult.DRAW.name
            else MatchResult.LOSE
        )
        match.goal_for = data_match[f"score.fullTime.{match.side.name.lower()}"]
        match.goal_against = data_match[
            f"score.fullTime.{"away" if match.side == MatchSide.HOME else "home"}"
        ]

        side = 0 if match.side == MatchSide.HOME else 1

        match.fouls = livescore_match[side]["Fls"]
        match.shots = (
            livescore_match[side]["Shof"]
            + livescore_match[side]["Shon"]
            + livescore_match[side]["Shbl"]
            + livescore_match[side]["Shwd"]
        )
        match.shots_off_goal = livescore_match[side]["Shof"]
        match.shots_on_goal = livescore_match[side]["Shon"]
        match.possession = livescore_match[side]["Pss"]
        match.livescore_xg = livescore_match[side].get("Xg", None)

        return match

    def _retrieve_matches(
        self, team: Team, season: int, now: datetime
    ) -> list[MatchStatistics]:
        matches = [m for m in team.matches if m.date < (now - timedelta(days=1))]
        logger.info(
            f"Extract [{len(matches)}] matches statistics of team [{team.short_name}]"
        )

        data_df = None
        if any(m for m in matches if m.status == MatchStatus.NO_DATA):
            data_df, _ = self.data_api.get_team_matches(team.data_id, season)

        statistics = []
        for match in matches:
            if match.status == MatchStatus.NO_DATA:
                logger.info(
                    f"No statistics found for match [{match.data_id}] of team [{team.short_name}], so extract from api"
                )
                data_match = data_df[data_df["id"] == match.data_id].iloc[0]
                livescore_match = self.livescore_api.get_match_statistics(
                    match.livescore_id
                )
                match = self._enrichment_match_statistics(
                    match, data_match, livescore_match
                )
                time.sleep(0.2)

            statistics.append(match)
        return statistics

    def get_match_data(
        self, home_team: Team, away_team: Team, season: int
    ) -> tuple[list[MatchStatistics], list[MatchStatistics]]:
        now = datetime.now()

        home_matches = self._retrieve_matches(home_team, season, now)
        away_matches = self._retrieve_matches(away_team, season, now)

        return home_matches, away_matches
