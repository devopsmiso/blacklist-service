"""Pruebas del punto de entrada WSGI y del arranque sin base de datos."""
import importlib
import sys

import pytest

from blacklist import create_app
from blacklist.infrastructure import database

DB_ENV = {
    "DB_USER": "postgres",
    "DB_PASSWORD": "postgres",
    "DB_HOST": "host-inexistente.invalid",
    "DB_NAME": "blacklist",
    "JWT_SECRET_KEY": "secret",
}


@pytest.fixture
def env(monkeypatch):
    for name, value in DB_ENV.items():
        monkeypatch.setenv(name, value)


def test_application_module_exposes_app_and_initializes_schema(env, monkeypatch):
    initialized = []
    monkeypatch.setattr(database, "init_db", initialized.append)
    monkeypatch.delitem(sys.modules, "application", raising=False)

    module = importlib.import_module("application")

    assert initialized == [module.application]


def test_generate_token_works_without_database_connection(env):
    app = create_app()

    result = app.test_cli_runner().invoke(args=["generate-token"])

    assert result.exit_code == 0
    assert result.output.count(".") == 2  # header.payload.firma
