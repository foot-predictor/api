import logging

import httpx

logger = logging.getLogger(__name__)


class LiveScoreApiService:
    def __init__(self, api_key: str, host: str, api_keys_spare: list[str] = None):
        self._api_key = api_key
        self._host = host
        self._retry_count = 0
        self._api_keys_spare = api_keys_spare

    def _request(
        self,
        uri: str,
        filters: dict[str, str | int] | None = None,
    ):
        response = httpx.get(
            f"https://{self._host}/{uri}",
            headers={
                "x-rapidapi-key": self._api_key,
                "x-rapidapi-host": self._host,
            },
            params=filters,
        )
        if response.status_code == 429:
            logger.info("Maximum requests reached, rotating API key.")
            for key in [self._api_key, *self._api_keys_spare]:
                if key == self._api_key:
                    continue
                self._api_key = key
                logging.info("Choosing new API key")
                return self._request(uri, filters)

        if response.status_code != 200:
            raise Exception(
                f"Request failed [{response.status_code}] : {response.json()}"
            )
        return response.json()

    def get_teams_details(self, team_id: int):
        response = self._request("teams/detail", filters={"ID": str(team_id)})
        return response

    def get_match_statistics(self, match_id: int) -> list[dict[str, int]]:
        try:
            response = self._request(
                "matches/v2/get-statistics",
                filters={"Eid": f"{match_id}", "Category": "soccer"},
            )
            self._retry_count = 0
            return response["Stat"]
        except httpx.ReadTimeout:
            if self._retry_count < 3:
                logger.info("Request timed out, retrying")
                self._retry_count += 1
                return self.get_match_statistics(match_id)
            else:
                raise Exception("Request timed out 3 times")
