import pytest

from app.services.ingestion.collector import SeedDataCollector
from app.services.ingestion.normalizer import normalize_skills, _generate_slug


class TestSlugGeneration:
    def test_basic_slug(self):
        assert _generate_slug("Code Reviewer") == "code-reviewer"

    def test_special_characters(self):
        assert _generate_slug("My Tool! @#$%") == "my-tool"

    def test_unicode(self):
        slug = _generate_slug("Café Résumé")
        assert slug == "cafe-resume"

    def test_multiple_spaces(self):
        assert _generate_slug("hello   world   test") == "hello-world-test"


class TestNormalizeSkills:
    def test_basic_normalization(self):
        skills = [{"name": "Test Skill", "slug": "test-skill"}]
        result = normalize_skills(skills)
        assert len(result) == 1
        assert result[0]["slug"] == "test-skill"
        assert result[0]["description"] == ""
        assert result[0]["tags"] == []

    def test_generates_slug_from_name(self):
        skills = [{"name": "My Cool Tool"}]
        result = normalize_skills(skills)
        assert result[0]["slug"] == "my-cool-tool"

    def test_deduplicates_by_slug(self):
        skills = [
            {"name": "Tool A", "slug": "same-slug"},
            {"name": "Tool B", "slug": "same-slug"},
        ]
        result = normalize_skills(skills)
        assert len(result) == 1
        assert result[0]["name"] == "Tool A"

    def test_skills_without_name_skipped(self):
        skills = [{"slug": "no-name"}, {"name": "Valid", "slug": "valid"}]
        result = normalize_skills(skills)
        assert len(result) == 1
        assert result[0]["name"] == "Valid"

    def test_sets_defaults(self):
        skills = [{"name": "Minimal"}]
        result = normalize_skills(skills)
        skill = result[0]
        assert skill["risk_level"] == "pending"
        assert skill["security_score"] == 0
        assert skill["downloads"] == 0
        assert skill["stars"] == 0
        assert skill["content"] == ""

    def test_preserves_existing_values(self):
        skills = [{
            "name": "Full Skill",
            "slug": "full-skill",
            "description": "A full skill",
            "tags": ["test"],
            "capabilities": ["file_read"],
            "risk_level": "safe",
            "security_score": 90,
        }]
        result = normalize_skills(skills)
        assert result[0]["description"] == "A full skill"
        assert result[0]["tags"] == ["test"]
        assert result[0]["risk_level"] == "safe"


class TestSeedDataCollector:
    async def test_collect_returns_copy(self):
        data = [{"name": "Skill 1", "slug": "skill-1"}]
        collector = SeedDataCollector(data)
        result = await collector.collect()
        assert len(result) == 1
        assert result[0] is not data[0]

    async def test_collect_empty(self):
        collector = SeedDataCollector([])
        result = await collector.collect()
        assert result == []


class TestNormalizerIntegration:
    async def test_collect_then_normalize(self):
        raw = [
            {"name": "Code Reviewer", "description": "Reviews code"},
            {"name": "Code Reviewer", "description": "Duplicate"},
            {"name": "Web Scraper", "tags": ["scraping"]},
        ]
        collector = SeedDataCollector(raw)
        collected = await collector.collect()
        normalized = normalize_skills(collected)

        assert len(normalized) == 2
        slugs = [s["slug"] for s in normalized]
        assert "code-reviewer" in slugs
        assert "web-scraper" in slugs
