import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill
from app.services.discovery.query_understanding import QueryUnderstanding, _fallback_understanding
from app.services.discovery.ranking import compute_ranking_score


class TestFallbackQueryUnderstanding:
    def test_basic_query(self):
        result = _fallback_understanding("python code review tool")
        assert "python" in result.keywords
        assert "code" in result.keywords or "review" in result.keywords
        assert "python" in result.tags

    def test_security_query(self):
        result = _fallback_understanding("security scanner for api testing")
        assert "security" in result.tags
        assert "api" in result.tags
        assert "network_access" in result.capabilities or "api" in result.keywords

    def test_devops_query(self):
        result = _fallback_understanding("docker deployment automation")
        assert "docker" in result.tags or "devops" in result.tags
        assert "automation" in result.tags or "devops" in result.tags

    def test_empty_query(self):
        result = _fallback_understanding("")
        assert result.keywords == []
        assert result.tags == []
        assert result.capabilities == []

    def test_stop_words_filtered(self):
        result = _fallback_understanding("how do i use the python tool")
        assert "how" not in result.keywords
        assert "the" not in result.keywords

    def test_max_tags_limit(self):
        result = _fallback_understanding("python javascript security docker git database api")
        assert len(result.tags) <= 5

    def test_intent_default(self):
        result = _fallback_understanding("test query")
        assert result.intent == "find_skill"


class TestRankingFormula:
    def _make_skill(self, **kwargs):
        defaults = {
            "name": "Test",
            "slug": "test",
            "description": "test",
            "author": "tester",
            "tags": ["python"],
            "capabilities": ["file_read"],
            "risk_level": "safe",
            "security_score": 80,
            "security_report": {},
            "downloads": 1000,
            "stars": 50,
            "install_count": 100,
            "version": "1.0.0",
            "content": "x" * 200,
        }
        defaults.update(kwargs)
        return Skill(**defaults)

    def test_safe_skill_scores_higher_than_risky(self):
        safe = self._make_skill(risk_level="safe", slug="safe")
        risky = self._make_skill(risk_level="high", slug="risky")
        safe_score = compute_ranking_score(safe, relevance_score=0.5)
        risky_score = compute_ranking_score(risky, relevance_score=0.5)
        assert safe_score > risky_score

    def test_high_relevance_boosts_score(self):
        skill = self._make_skill()
        low = compute_ranking_score(skill, relevance_score=0.1)
        high = compute_ranking_score(skill, relevance_score=0.9)
        assert high > low

    def test_popular_skill_scores_higher(self):
        popular = self._make_skill(downloads=50000, stars=5000, slug="popular")
        unpopular = self._make_skill(downloads=10, stars=1, slug="unpopular")
        pop_score = compute_ranking_score(popular, relevance_score=0.5)
        unpop_score = compute_ranking_score(unpopular, relevance_score=0.5)
        assert pop_score > unpop_score

    def test_score_bounded_0_to_1(self):
        skill = self._make_skill(downloads=100000, stars=10000, security_score=100, risk_level="safe")
        score = compute_ranking_score(skill, relevance_score=1.0)
        assert 0.0 <= score <= 1.0

    def test_zero_relevance_still_scores(self):
        skill = self._make_skill()
        score = compute_ranking_score(skill, relevance_score=0.0)
        assert score >= 0.0

    def test_quality_factors(self):
        full = self._make_skill(version="1.0", content="x" * 200, tags=["a", "b", "c"], capabilities=["a", "b"], security_score=90, slug="full")
        minimal = self._make_skill(version=None, content=None, tags=[], capabilities=[], security_score=20, slug="minimal")
        assert compute_ranking_score(full, 0.5) > compute_ranking_score(minimal, 0.5)


@pytest.fixture(autouse=True)
async def clean_db(db_session: AsyncSession):
    await db_session.execute(text("DELETE FROM skills"))
    await db_session.commit()


class TestSearchEndpoint:
    async def test_search_returns_query_understanding(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=python+testing")
        assert resp.status_code == 200
        body = resp.json()
        assert "query_understanding" in body
        assert "tags" in body["query_understanding"]
        assert "capabilities" in body["query_understanding"]

    async def test_search_finds_by_name(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=Alpha")
        body = resp.json()
        assert body["meta"]["total"] >= 1
        slugs = [s["slug"] for s in body["data"]]
        assert "alpha-skill" in slugs

    async def test_search_finds_by_description(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=medium+risk")
        body = resp.json()
        slugs = [s["slug"] for s in body["data"]]
        assert "beta-skill" in slugs

    async def test_search_no_results(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=nonexistentxyz")
        body = resp.json()
        assert body["meta"]["total"] == 0
        assert body["data"] == []

    async def test_search_results_have_ranking_score(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=skill")
        body = resp.json()
        for skill in body["data"]:
            assert "rankingScore" in skill

    async def test_search_pagination(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/skills/search?q=skill&page_size=1")
        body = resp.json()
        assert len(body["data"]) == 1
        assert body["meta"]["total"] >= 2
        assert body["meta"]["page_size"] == 1

    async def test_search_empty_query_rejected(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills/search?q=")
        assert resp.status_code == 422

    async def test_search_missing_query_rejected(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills/search")
        assert resp.status_code == 422


class TestRecommendationsEndpoint:
    async def test_empty_recommendations(self, client: AsyncClient):
        resp = await client.get("/api/v1/recommendations")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"] == []

    async def test_recommendations_with_data(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/recommendations")
        assert resp.status_code == 200
        body = resp.json()
        assert len(body["data"]) > 0

    async def test_recommendations_excludes_critical(self, client: AsyncClient, db_session: AsyncSession):
        safe = Skill(
            name="Safe One", slug="safe-one", description="safe skill",
            author="A", tags=["python"], capabilities=["file_read"],
            risk_level="safe", security_score=95, security_report={},
            downloads=100, stars=10,
        )
        critical = Skill(
            name="Critical One", slug="critical-one", description="critical skill",
            author="B", tags=["evil"], capabilities=["code_exec"],
            risk_level="critical", security_score=10, security_report={},
            downloads=100, stars=10,
        )
        db_session.add_all([safe, critical])
        await db_session.flush()

        resp = await client.get("/api/v1/recommendations")
        body = resp.json()
        slugs = [s["slug"] for s in body["data"]]
        assert "safe-one" in slugs
        assert "critical-one" not in slugs

    async def test_recommendations_limit(self, client: AsyncClient, seed_skills):
        resp = await client.get("/api/v1/recommendations?limit=1")
        body = resp.json()
        assert len(body["data"]) <= 1
