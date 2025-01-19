import httpx


class TransfermarktApiService:
    def __init__(self, api_key: str, host: str):
        self._api_key = api_key
        self._host = host

    def _request(self, uri: str, filters: dict[str, str | int] | None = None):
        params = {"locale": "FR"}
        if filters:
            params.update(filters)

        response = httpx.get(
            f"https://{self._host}/{uri}",
            headers={
                "x-rapidapi-key": self._api_key,
                "x-rapidapi-host": self._host,
            },
            params=params,
        )
        if response.status_code != 200:
            raise Exception(
                f"Request failed [{response.status_code}] : {response.json()}"
            )
        return response.json()

    def get_match_statistics(self, match_id: int, season: int):
        response = self._request(
            "/v1/fixtures/statistics",
            filters={"club_id": f"{match_id}", "season_id": f"{season}"},
        )
        return response
