from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest
from sqlalchemy.exc import OperationalError

from blacklist.domain.entities import BlacklistEntry
from blacklist.domain.exceptions import EmailAlreadyBlacklistedError
from blacklist.extensions import db
from blacklist.infrastructure.sqlalchemy_blacklist_repository import (
    SQLAlchemyBlacklistRepository,
)


def _entry(email="user@example.com"):
    return BlacklistEntry(
        email=email,
        app_uuid="9f1c3a52-7d4b-4c1e-9a3f-2b8e6d0c1a77",
        blocked_reason="Spam",
        ip_address="10.0.0.1",
        created_at=datetime(2026, 10, 12, tzinfo=timezone.utc),
    )


def test_add_and_find_by_email(app):
    with app.app_context():
        repository = SQLAlchemyBlacklistRepository(db.session)

        saved = repository.add(_entry())
        found = repository.find_by_email("user@example.com")

    assert saved.id is not None
    assert found.id == saved.id
    assert found.ip_address == "10.0.0.1"
    assert found.blocked_reason == "Spam"


def test_find_by_email_returns_none_when_missing(app):
    with app.app_context():
        assert SQLAlchemyBlacklistRepository(db.session).find_by_email("x@y.com") is None


def test_add_duplicate_raises_domain_error(app):
    with app.app_context():
        repository = SQLAlchemyBlacklistRepository(db.session)
        repository.add(_entry())

        with pytest.raises(EmailAlreadyBlacklistedError):
            repository.add(_entry())


def test_add_rolls_back_and_reraises_database_errors():
    session = MagicMock()
    session.commit.side_effect = OperationalError("INSERT", {}, Exception("down"))

    with pytest.raises(OperationalError):
        SQLAlchemyBlacklistRepository(session).add(_entry())

    session.rollback.assert_called_once()
