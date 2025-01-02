import logging
from datetime import datetime
from typing import Literal

import httpx
import pandas as pd

API_URL = "https://api.football-data.org/v4/"
LeagueType = Literal[
    "PL",  # Premier League England
    "CL",  # Champions League
    "FL1",  # Ligue 1 France
    "BL1",  # Bundesliga Germany
    "SA",  # Serie A Italy
    "PD",  # La Liga Spain
    "EL",  # Europa League
    "WC",  # World Cup
]

logger = logging.getLogger(__name__)


class FootballDataApiService:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def _requests(self, uri) -> dict:
        response = httpx.get(
            f"{API_URL}/{uri}",
            headers={"X-Auth-Token": self._api_key},
        )
        if response.status_code != 200:
            logger.error(f"Request failed [{response.status_code}] : {response.json()}")
            raise Exception(
                f"Request failed [{response.status_code}] : {response.json()}"
            )

        return response.json()

    def get_league(self, league: LeagueType) -> dict[str, str]:
        response = self._requests(f"competitions/{league}")
        return {
            "name": response["name"],
            "logo_url": response["emblem"],
            "code": response["code"],
            "start_date": response["currentSeason"]["startDate"],
        }

    def get_league_teams(self, league: LeagueType) -> list[dict[str, str]]:
        response = self._requests(
            f"competitions/{league}/teams?season={datetime.now().year}",
        )
        return [
            {"name": team["name"], "logo_url": team["crest"], "id": team["id"]}
            for team in response["teams"]
        ]

    def get_team_matches(
        self, team_id: int, season: int
    ) -> tuple[pd.DataFrame, dict[str, str | int]]:
        logger.info(f"Getting matches for team [{team_id}] for season [{season}]")
        response = self._requests(
            f"teams/{team_id}/matches?season={season}&status=FINISHED",
        )

        df = pd.DataFrame(pd.json_normalize(response["matches"]))
        df = df.filter(
            [
                "id",
                "matchday",
                "homeTeam.id",
                "homeTeam.name",
                "homeTeam.crest",
                "awayTeam.id",
                "awayTeam.name",
                "awayTeam.crest",
                "score.winner",
                "score.fullTime.home",
                "score.fullTime.away",
            ],
            axis=1,
        )
        return df, response["resultSet"]
