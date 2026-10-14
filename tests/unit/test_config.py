import logging

import pytest

from blacklist.config import Config, build_database_uri
from blacklist.logging_config import configure_logging

DB_ENV = {
    "DB_USER": "postgres",
    "DB_PASSWORD": "p@ss:w/rd",
    "DB_HOST": "localhost",
    "DB_NAME": "blacklist",
}


@pytest.fixture
def db_env(monkeypatch):
    for name, value in DB_ENV.items():
        monkeypatch.setenv(name, value)
    for name in ("DB_PORT", "LOG_LEVEL", "PROXY_FIX_X_FOR"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setenv("JWT_SECRET_KEY", "secret")


def test_build_database_uri_escapes_password_and_uses_default_port(db_env):
    assert (
        build_database_uri()
        == "postgresql://postgres:p%40ss%3Aw%2Frd@localhost:5432/blacklist"
    )


def test_build_database_uri_uses_custom_port(db_env, monkeypatch):
    monkeypatch.setenv("DB_PORT", "5433")

    assert build_database_uri().endswith("@localhost:5433/blacklist")


def test_missing_required_variable_raises(db_env, monkeypatch):
    monkeypatch.delenv("DB_HOST")

    with pytest.raises(RuntimeError, match="DB_HOST"):
        build_database_uri()


def test_config_reads_environment_with_defaults(db_env):
    config = Config()

    assert config.JWT_SECRET_KEY == "secret"
    assert config.LOG_LEVEL == "INFO"
    assert config.PROXY_FIX_X_FOR == 1
    assert config.JWT_ACCESS_TOKEN_EXPIRES is False


def test_config_requires_jwt_secret(db_env, monkeypatch):
    monkeypatch.delenv("JWT_SECRET_KEY")

    with pytest.raises(RuntimeError, match="JWT_SECRET_KEY"):
        Config()


def test_configure_logging_sets_root_level():
    configure_logging("warning")

    assert logging.getLogger().level == logging.WARNING
