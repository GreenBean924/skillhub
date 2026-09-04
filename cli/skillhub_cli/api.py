import httpx

DEFAULT_API_URL = "http://localhost:8000/api/v1"


class SkillHubAPI:
    def __init__(self, base_url: str | None = None):
        self._base_url = (base_url or DEFAULT_API_URL).rstrip("/")
        self._client = httpx.Client(timeout=30.0)

    def _headers(self) -> dict[str, str]:
        from skillhub_cli import __version__
        return {"X-SkillHub-CLI-Version": __version__}

    def get_skill(self, slug: str) -> dict:
        resp = self._client.get(f"{self._base_url}/skills/{slug}", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def install_skill(self, slug: str) -> dict:
        resp = self._client.get(f"{self._base_url}/skills/{slug}/install", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def search_skills(self, query: str, page_size: int = 20) -> dict:
        resp = self._client.get(
            f"{self._base_url}/skills/search",
            params={"q": query, "page_size": page_size},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def list_skills(self, page: int = 1, page_size: int = 20, sort_by: str = "downloads", order: str = "desc") -> dict:
        resp = self._client.get(
            f"{self._base_url}/skills",
            params={"page": page, "page_size": page_size, "sort_by": sort_by, "order": order},
            headers=self._headers(),
        )
        resp.raise_for_status()
        return resp.json()

    def get_stats(self) -> dict:
        resp = self._client.get(f"{self._base_url}/stats", headers=self._headers())
        resp.raise_for_status()
        return resp.json()

    def close(self):
        self._client.close()
