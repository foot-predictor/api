import logging
import re
from datetime import date
from typing import Any

import httpx
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

API_URL = "https://apiv3.apifootball.com"
LEAGUES_IDS = {
    "Premier League": 152,
    "Ligue 1": 168,
    "Bundesliga": 175,
    "Serie A": 207,
    "La Liga": 302,
    "Champions league": 3,
    "Europa League": 4,
    "World Cup": 28,
}


class FootballStatsApiService:
    def __init__(self, api_key: str):
        self._api_key = api_key

    def _request(
        self, action_name: str, filters: dict[str, str | int] | None = None
    ) -> Any:
        params: dict[str, str | int] = {
            "action": action_name,
            "APIkey": self._api_key,
        }
        if filters is not None:
            params.update(filters)

        response = httpx.get(
            f"{API_URL}/?{"&".join(f"{key}={value}" for key, value in params.items())}"
        )
        if response.status_code != 200:
            logger.error(f"Request failed [{response.status_code}] : {response.json()}")
            raise Exception(
                f"Request failed [{response.status_code}] : {response.json()}"
            )

        return response.json()

    @staticmethod
    def _flatten_statistics(row: pd.Series) -> pd.Series:
        statistics = {}
        for stat in row["statistics"]:
            home_stat_key = f"home.{stat['type'].lower().replace(' ', '_')}"
            away_stat_key = f"away.{stat['type'].lower().replace(' ', '_')}"

            if home_stat_key not in statistics:
                result = re.search(r"\d+", stat["home"])
                statistics[home_stat_key] = (
                    int(result.group()) if result is not None else np.nan
                )
            if away_stat_key not in statistics:
                result = re.search(r"\d+", stat["away"])
                statistics[away_stat_key] = (
                    int(result.group()) if result is not None else np.nan
                )

            if (
                (stat["home"] != "0" or stat["away"] != "0")
                and statistics[home_stat_key] == "0"
                and statistics[away_stat_key] == "0"
            ):
                result = re.search(r"\d+", stat["home"])
                statistics[home_stat_key] = (
                    int(result.group()) if result is not None else np.nan
                )
                result = re.search(r"\d+", stat["away"])
                statistics[away_stat_key] = (
                    int(result.group()) if result is not None else np.nan
                )

        return pd.Series(statistics)

    def get_team_matches_statistics(
        self, team_id: int, from_date: date, to_date: date | None = None
    ) -> pd.DataFrame:
        logger.info(f"Getting statistics for team [{team_id}]")
        responses = self._request(
            "get_events",
            filters={
                "team_id": team_id,
                "from": from_date.strftime("%Y-%m-%d"),
                "to": (to_date or date.today()).strftime("%Y-%m-%d"),
            },
        )

        df = pd.DataFrame(pd.json_normalize(responses))
        df = df.filter(
            ["match_round", "statistics"],
            axis=1,
        )
        # Convert String to Int
        df["match_round"] = pd.to_numeric(df["match_round"], errors="coerce")

        # Distribute and flatten statistics
        stats_df = df.apply(self._flatten_statistics, axis=1)
        result_df = pd.concat([df.drop("statistics", axis=1), stats_df], axis=1)

        return result_df
