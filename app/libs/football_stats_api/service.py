import re
from datetime import date

import httpx
import pandas as pd

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

    def _request(self, action_name: str, filters: dict[str, str] | None = None):
        params = {
            "action": action_name,
            "APIkey": self._api_key,
        }
        if filters is not None:
            params.update(filters)

        response = httpx.get(
            f"{API_URL}/?{"&".join(f"{key}={value}" for key, value in params.items())}"
        )
        if response.status_code != 200:
            raise Exception(
                f"Request failed [{response.status_code}] : {response.json()}"
            )

        return response.json()

    def _flatten_statistics(self, row: pd.Series) -> pd.Series:
        flattened = {}
        statistics = {}
        for stat in row["statistics"]:
            if stat["type"] not in statistics:
                statistics[stat["type"]] = stat
            else:
                if (
                    statistics[stat["type"]]["away"] == "0"
                    and statistics[stat["type"]]["home"] == "0"
                ):
                    statistics[stat["type"]] = stat

        for stat in statistics.values():
            flattened[f"home.{stat["type"].lower().replace(' ', '_')}"] = int(
                re.search(r"\d+", stat["home"]).group()
            )
            flattened[f"away.{stat["type"].lower().replace(' ', '_')}"] = int(
                re.search(r"\d+", stat["away"]).group()
            )

        return pd.Series(flattened)

    def get_team_matches_statistics(
        self, team_id: int, from_date: date, to_date: date | None = None
    ):
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
        stats_df = stats_df.fillna(0)
        result_df = pd.concat([df.drop("statistics", axis=1), stats_df], axis=1)

        return result_df

        # return pd.DataFrame(pd.json_normalize(responses))
