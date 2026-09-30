import asyncio

import httpx

from app.main import app


def get(path: str) -> httpx.Response:
    async def request() -> httpx.Response:
        transport = httpx.ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.get(path)

    return asyncio.run(request())


def test_health_is_independent_and_healthy():
    """Catch health checks that fail because they depend on optional configuration."""
    response = get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_version_is_a_string():
    """Catch image or artifact builds that omit the deployment version contract."""
    response = get("/api/version")

    assert response.status_code == 200
    assert response.json() == {"version": "dev"}


def test_config_exposes_environment_without_secrets():
    """Catch diagnostics that accidentally disclose process environment variables."""
    response = get("/api/config")

    assert response.status_code == 200
    assert response.json() == {"environment": "local"}
