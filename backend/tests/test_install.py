import pytest
from httpx import AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.skill import Skill


@pytest.fixture(autouse=True)
async def clean_db(db_session: AsyncSession):
    await db_session.execute(text("DELETE FROM install_logs"))
    await db_session.execute(text("DELETE FROM skills"))
    await db_session.commit()


@pytest.fixture
async def seed_skill(db_session: AsyncSession) -> Skill:
    skill = Skill(
        name="Test Skill",
        slug="test-skill",
        description="A test skill",
        author="Tester",
        tags=["python"],
        capabilities=["file_read"],
        risk_level="safe",
        security_score=95,
        security_report={"findings": [], "scannedAt": "2026-09-01T00:00:00"},
        install_command="skillhub install test-skill",
        downloads=100,
        stars=10,
        skill_md="# Test Skill\nA test skill.",
    )
    db_session.add(skill)
    await db_session.flush()
    return skill


class TestInstallEndpoint:
    async def test_install_existing(self, client: AsyncClient, seed_skill):
        resp = await client.get("/api/v1/skills/test-skill/install")
        assert resp.status_code == 200
        body = resp.json()
        assert body["slug"] == "test-skill"
        assert body["skill_md"] == "# Test Skill\nA test skill."
        assert body["risk_level"] == "safe"
        assert body["security_score"] == 95
        assert body["agent_type"] == "claude_code"

    async def test_install_not_found(self, client: AsyncClient):
        resp = await client.get("/api/v1/skills/nonexistent/install")
        assert resp.status_code == 404

    async def test_install_increments_count(self, client: AsyncClient, seed_skill, db_session: AsyncSession):
        await client.get("/api/v1/skills/test-skill/install")
        await db_session.refresh(seed_skill)
        assert seed_skill.install_count == 1

    async def test_install_creates_log(self, client: AsyncClient, seed_skill, db_session: AsyncSession):
        await client.get("/api/v1/skills/test-skill/install")
        result = await db_session.execute(text("SELECT COUNT(*) FROM install_logs"))
        count = result.scalar()
        assert count == 1

    async def test_install_response_fields(self, client: AsyncClient, seed_skill):
        resp = await client.get("/api/v1/skills/test-skill/install")
        body = resp.json()
        for field in ["slug", "skill_md", "install_command", "risk_level", "security_score", "agent_type", "message"]:
            assert field in body


class TestAdapterUnit:
    async def test_claude_code_adapter_detect(self, tmp_path):
        from app.services.installation.claude_code import ClaudeCodeAdapter
        adapter = ClaudeCodeAdapter()
        env = await adapter.detect_environment()
        assert env.agent_type.value == "claude_code"

    async def test_claude_code_adapter_install_and_verify(self, tmp_path):
        from app.services.installation.claude_code import ClaudeCodeAdapter

        adapter = ClaudeCodeAdapter()
        import app.services.installation.claude_code as cc_mod
        original_dir = cc_mod.SKILL_DIR
        cc_mod.SKILL_DIR = tmp_path / "skills"

        try:
            result = await adapter.install_skill("test-skill", "# Test\nContent")
            assert result.success
            assert result.slug == "test-skill"

            verified = await adapter.verify_installation("test-skill")
            assert verified

            installed = await adapter.list_skills()
            assert "test-skill" in installed

            uninstalled = await adapter.uninstall_skill("test-skill")
            assert uninstalled

            verified_after = await adapter.verify_installation("test-skill")
            assert not verified_after
        finally:
            cc_mod.SKILL_DIR = original_dir

    async def test_uninstall_nonexistent(self):
        from app.services.installation.claude_code import ClaudeCodeAdapter

        adapter = ClaudeCodeAdapter()
        import app.services.installation.claude_code as cc_mod
        original_dir = cc_mod.SKILL_DIR
        cc_mod.SKILL_DIR = __import__("pathlib").Path("/tmp/nonexistent_skillhub_test")

        try:
            result = await adapter.uninstall_skill("nonexistent")
            assert not result
        finally:
            cc_mod.SKILL_DIR = original_dir

    def test_adapter_factory(self):
        from app.services.installation.factory import AdapterFactory
        from app.services.installation.adapter import AgentType
        from app.services.installation.claude_code import ClaudeCodeAdapter

        adapter = AdapterFactory.create(AgentType.CLAUDE_CODE)
        assert isinstance(adapter, ClaudeCodeAdapter)

    def test_adapter_factory_invalid_type(self):
        from app.services.installation.factory import AdapterFactory
        with pytest.raises(ValueError):
            AdapterFactory.create("invalid_type")
