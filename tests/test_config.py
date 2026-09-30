from app.config import Settings


def test_settings_use_safe_defaults(monkeypatch):
    """Catch deployments that accidentally require unset environment variables."""
    monkeypatch.delenv("APP_VERSION", raising=False)
    monkeypatch.delenv("APP_ENV", raising=False)

    settings = Settings.from_env()

    assert settings.version == "dev"
    assert settings.environment == "local"


def test_settings_read_deployment_environment(monkeypatch):
    """Catch deployments that ignore the version and environment injected by AWS."""
    monkeypatch.setenv("APP_VERSION", "a1b2c3d4e5f6")
    monkeypatch.setenv("APP_ENV", "dev")

    settings = Settings.from_env()

    assert settings.version == "a1b2c3d4e5f6"
    assert settings.environment == "dev"
