import pytest
from pydantic import ValidationError

from probable_cause.config import Settings


@pytest.fixture(autouse=True)
def clean_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove settings env vars so tests don't depend on the developer's shell or .env."""
    for name in Settings.model_fields:
        monkeypatch.delenv(name.upper(), raising=False)


def test_database_url_built_from_parts(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("POSTGRES_PORT", "5433")

    settings = Settings(_env_file=None)

    expected = "postgresql://probable_cause:secret@127.0.0.1:5433/probable_cause"
    assert settings.database_url == expected


def test_password_special_characters_are_url_encoded(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_PASSWORD", "p@ss:w/rd")

    settings = Settings(_env_file=None)

    assert "p%40ss%3Aw%2Frd@" in settings.database_url


def test_secrets_hidden_from_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test")

    settings = Settings(_env_file=None)

    assert "secret" not in repr(settings)
    assert "sk-test" not in repr(settings)


def test_missing_password_is_an_error() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_invalid_llm_provider_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("POSTGRES_PASSWORD", "secret")
    monkeypatch.setenv("LLM_PROVIDER", "gemini")

    with pytest.raises(ValidationError):
        Settings(_env_file=None)
