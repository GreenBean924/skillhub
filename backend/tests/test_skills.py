import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.fixture(autouse=True)
async def clean_db(db_session: AsyncSession):
    await db_session.execute(text("DELETE FROM skills"))
    await db_session.commit()


class TestHealthCheck:
    async def test_health(self, client: AsyncClient):
        resp = await client.get("/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


class TestListSkills:
    async def test_empty_list(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"] == []
        assert body["meta"]["total"] == 0

    async def test_list_with_data(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) == 3
        assert body["meta"]["total"] == 3
        assert body["meta"]["page"] == 1
        assert body["meta"]["page_size"] == 20

    async def test_pagination(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills?page=1&page_size=2")
        body = resp.json()
        assert len(body["data"]) == 2
        assert body["meta"]["total"] == 3
        assert body["meta"]["page_size"] == 2

        resp2 = await client.get("/api/v1/skills?page=2&page_size=2")
        body2 = resp2.json()
        assert len(body2["data"]) == 1

    async def test_page_size_limit(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills?page_size=100")
        assert resp.status_code == 422

    async def test_invalid_page(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills?page=0")
        assert resp.status_code == 422

    async def test_sort_order(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills?sort_by=stars&order=desc")
        body = resp.json()
        stars = [s["stars"] for s in body["data"]]
        assert stars == sorted(stars, reverse=True)

    async def test_response_fields(self, client: AsyncClient, seed_skill):
        resp = await client.get("/api/v1/skills")
        skill = resp.json()["data"][0]
        assert "slug" in skill
        assert "name" in skill
        assert "security" in skill
        assert "level" in skill["security"]
        assert "score" in skill["security"]
        assert "findings" in skill["security"]


class TestGetSkill:
    async def test_get_existing(self, client: AsyncClient, seed_skill):
        resp = await client.get("/api/v1/skills/test-skill")
        assert resp.status_code == 200
        body = resp.json()
        assert body["slug"] == "test-skill"
        assert body["name"] == "Test Skill"
        assert body["author"] == "Test Author"
        assert body["downloads"] == 1200
        assert body["stars"] == 42

    async def test_get_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills/nonexistent")
        assert resp.status_code == 404

    async def test_security_report(self, client: AsyncClient, seed_skill):
        resp = await client.get("/api/v1/skills/test-skill")
        security = resp.json()["security"]
        assert security["level"] == "safe"
        assert security["score"] == 95
        assert len(security["findings"]) == 1
        assert security["findings"][0]["id"] == "F001"

    async def test_tags_and_capabilities(self, client: AsyncClient, seed_skill):
        resp = await client.get("/api/v1/skills/test-skill")
        body = resp.json()
        assert body["tags"] == ["python", "testing"]
        assert body["capabilities"] == ["file_read", "code_exec"]


class TestSearchSkills:
    async def test_search_by_name(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=Alpha")
        assert resp.status_code == 200
        body = resp.json()
        assert body["meta"]["total"] >= 1
        slugs = [s["slug"] for s in body["data"]]
        assert "alpha-skill" in slugs

    async def test_search_by_description(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=medium+risk")
        body = resp.json()
        assert body["meta"]["total"] >= 1
        slugs = [s["slug"] for s in body["data"]]
        assert "beta-skill" in slugs

    async def test_search_no_results(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=nonexistent")
        body = resp.json()
        assert body["meta"]["total"] == 0
        assert body["data"] == []

    async def test_search_empty_query(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills/search?q=")
        assert resp.status_code == 422

    async def test_search_missing_query(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills/search")
        assert resp.status_code == 422

    async def test_search_pagination(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=skill&page_size=1")
        body = resp.json()
        assert len(body["data"]) == 1
        assert body["meta"]["total"] >= 2

    async def test_search_query_understanding(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=test")
        body = resp.json()
        assert "query_understanding" in body
        assert "tags" in body["query_understanding"]
        assert "capabilities" in body["query_understanding"]


class TestListTags:
    async def test_empty_tags(self, client: AsyncClient):
        resp = await client.get("/api/v1/tags")
        assert resp.status_code == 200
        assert resp.json()["data"] == []

    async def test_tags_with_counts(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/tags")
        body = resp.json()
        tags = {t["name"]: t["count"] for t in body["data"]}
        assert tags["python"] == 2
        assert tags["ai"] == 1
        assert tags["security"] == 1

    async def test_tags_sorted_by_count(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/tags")
        tags = resp.json()["data"]
        counts = [t["count"] for t in tags]
        assert counts == sorted(counts, reverse=True)


class TestGetStats:
    async def test_empty_stats(self, client: AsyncClient):
        resp = await client.get("/api/v1/stats")
        assert resp.status_code == 200
        body = resp.json()
        assert body["total_skills"] == 0
        assert body["safe_skills"] == 0
        assert body["total_downloads"] == 0

    async def test_stats_with_data(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/stats")
        body = resp.json()
        assert body["total_skills"] == 3
        assert body["safe_skills"] == 2
        assert body["total_downloads"] == 1500
        assert body["last_updated"] is not None

    async def test_stats_fields(self, client: AsyncClient, seed_skill):
        resp = await client.get("/api/v1/stats")
        body = resp.json()
        assert "total_skills" in body
        assert "safe_skills" in body
        assert "total_downloads" in body
        assert "last_updated" in body
