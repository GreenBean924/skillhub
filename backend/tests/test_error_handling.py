import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app

TEMP_PATH = "/__test_error__"


@pytest.fixture
async def error_client():
    """Client that surfaces the app's 500 response instead of re-raising."""

    @app.get(TEMP_PATH)
    async def boom():
        raise RuntimeError("kaboom-secret-detail")

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.router.routes = [r for r in app.router.routes if getattr(r, "path", None) != TEMP_PATH]


class TestGlobalErrorHandler:
    async def test_unhandled_returns_unified_500(self, error_client: AsyncClient):
        resp = await error_client.get(TEMP_PATH)
        assert resp.status_code == 500
        body = resp.json()
        assert body["error"]["code"] == "INTERNAL_ERROR"
        assert body["error"]["message"]

    async def test_does_not_leak_internals(self, error_client: AsyncClient):
        resp = await error_client.get(TEMP_PATH)
        assert "kaboom-secret-detail" not in resp.text
        assert "Traceback" not in resp.text
