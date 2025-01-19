import httpx


class LiveScoreApiService:
    def __init__(self, api_key: str, host: str):
        self._api_key = api_key
        self._host = host

    def _request(self, uri: str, filters: dict[str, str | int] | None = None):
        response = httpx.get(
            f"https://{self._host}/{uri}",
            headers={
                "x-rapidapi-key": self._api_key,
                "x-rapidapi-host": self._host,
            },
            params=filters,
        )
        if response.status_code != 200:
            raise Exception(
                f"Request failed [{response.status_code}] : {response.json()}"
            )
        return response.json()

    def get_teams_details(self, team_id: int):
        response = self._request("teams/details", filters={"ID": str(team_id)})
        return response

    def get_match_statistics(self, match_id: int):
        response = self._request(
            "matches/v2/get-statistics",
            filters={"Eid": f"{match_id}", "Category": "soccer"},
        )
        return response
