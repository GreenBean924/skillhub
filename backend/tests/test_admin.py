import pytest
from httpx import AsyncClient

import app.api.v1.admin as admin_mod


@pytest.fixture
def admin_settings(monkeypatch):
    """Point the admin module's settings at a known key/environment."""
    def _set(key: str, environment: str) -> None:
        monkeypatch.setattr(admin_mod.settings, "ADMIN_API_KEY", key)
        monkeypatch.setattr(admin_mod.settings, "ENVIRONMENT", environment)
    return _set


class TestAdminAuth:
    async def test_denied_without_key_when_configured(self, client: AsyncClient, admin_settings):
        admin_settings("s3cret", "production")
        resp = await client.post("/admin/ingest/skills-sh")
        assert resp.status_code == 403

    async def test_denied_with_wrong_key(self, client: AsyncClient, admin_settings):
        admin_settings("s3cret", "production")
        resp = await client.post(
            "/admin/ingest/skills-sh", headers={"X-Admin-Key": "wrong"}
        )
        assert resp.status_code == 403

    async def test_denied_in_production_when_key_unset(self, client: AsyncClient, admin_settings):
        admin_settings("", "production")
        resp = await client.post(
            "/admin/ingest/skills-sh", headers={"X-Admin-Key": "anything"}
        )
        assert resp.status_code == 403

    async def test_authorized_passes_gate(self, client: AsyncClient, admin_settings, monkeypatch):
        admin_settings("s3cret", "production")
        # Stub the background task so auth is exercised without triggering network ingestion.
        monkeypatch.setattr(admin_mod.BackgroundTasks, "add_task", lambda self, fn: None)
        resp = await client.post(
            "/admin/ingest/skills-sh", headers={"X-Admin-Key": "s3cret"}
        )
        assert resp.status_code == 200
        assert resp.json()["message"].startswith("Ingestion pipeline started")

    async def test_authorized_rejects_bad_max_skills(self, client: AsyncClient, admin_settings):
        admin_settings("s3cret", "production")
        resp = await client.post(
            "/admin/ingest/skills-sh?max_skills=999",
            headers={"X-Admin-Key": "s3cret"},
        )
        assert resp.status_code == 400
