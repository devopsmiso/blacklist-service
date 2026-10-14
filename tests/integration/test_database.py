import pytest
from sqlalchemy.exc import OperationalError

from blacklist.extensions import db
from blacklist.infrastructure.database import init_db

DB_ERROR = OperationalError("CREATE TABLE", {}, Exception("already exists"))


def test_init_db_retries_once_after_failure(app, monkeypatch):
    calls = []

    def flaky_create_all():
        calls.append(1)
        if len(calls) == 1:
            raise DB_ERROR

    monkeypatch.setattr(db, "create_all", flaky_create_all)

    init_db(app)

    assert len(calls) == 2


def test_init_db_raises_when_retry_fails(app, monkeypatch):
    def failing_create_all():
        raise DB_ERROR

    monkeypatch.setattr(db, "create_all", failing_create_all)

    with pytest.raises(OperationalError):
        init_db(app)
