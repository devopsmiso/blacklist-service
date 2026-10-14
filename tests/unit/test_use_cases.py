from dataclasses import replace
from datetime import datetime, timezone
from typing import Dict, Optional

import pytest

from blacklist.domain.entities import BlacklistEntry
from blacklist.domain.exceptions import EmailAlreadyBlacklistedError
from blacklist.domain.repository import BlacklistRepository
from blacklist.use_cases.add_email_to_blacklist import (
    AddEmailCommand,
    AddEmailToBlacklist,
    utc_now,
)
from blacklist.use_cases.get_blacklist_status import GetBlacklistStatus

FIXED_NOW = datetime(2026, 10, 12, 18, 0, tzinfo=timezone.utc)


class InMemoryBlacklistRepository(BlacklistRepository):
    """Doble de prueba: demuestra que los casos de uso no dependen de la BD."""

    def __init__(self) -> None:
        self.entries: Dict[str, BlacklistEntry] = {}

    def add(self, entry: BlacklistEntry) -> BlacklistEntry:
        saved = replace(entry, id=len(self.entries) + 1)
        self.entries[saved.email] = saved
        return saved

    def find_by_email(self, email: str) -> Optional[BlacklistEntry]:
        return self.entries.get(email)


@pytest.fixture
def repository():
    return InMemoryBlacklistRepository()


def _command(email="User@Example.com", reason="Spam"):
    return AddEmailCommand(
        email=email,
        app_uuid="9f1c3a52-7d4b-4c1e-9a3f-2b8e6d0c1a77",
        blocked_reason=reason,
        ip_address="10.0.0.1",
    )


def test_add_email_saves_normalized_entry_with_ip_and_timestamp(repository):
    use_case = AddEmailToBlacklist(repository, clock=lambda: FIXED_NOW)

    entry = use_case.execute(_command())

    assert entry.id == 1
    assert entry.email == "user@example.com"
    assert entry.ip_address == "10.0.0.1"
    assert entry.blocked_reason == "Spam"
    assert entry.created_at == FIXED_NOW
    assert repository.find_by_email("user@example.com") == entry


def test_add_email_rejects_duplicates_case_insensitive(repository):
    use_case = AddEmailToBlacklist(repository, clock=lambda: FIXED_NOW)
    use_case.execute(_command(email="user@example.com"))

    with pytest.raises(EmailAlreadyBlacklistedError):
        use_case.execute(_command(email="USER@example.com"))


def test_add_email_uses_utc_clock_by_default(repository):
    entry = AddEmailToBlacklist(repository).execute(_command(reason=None))

    assert entry.created_at.tzinfo == timezone.utc
    assert entry.blocked_reason is None


def test_utc_now_returns_aware_datetime():
    assert utc_now().tzinfo == timezone.utc


def test_get_status_returns_true_with_reason(repository):
    AddEmailToBlacklist(repository).execute(_command())

    status = GetBlacklistStatus(repository).execute(" USER@example.com ")

    assert status.email == "user@example.com"
    assert status.is_blacklisted is True
    assert status.blocked_reason == "Spam"


def test_get_status_returns_false_when_email_not_found(repository):
    status = GetBlacklistStatus(repository).execute("nobody@example.com")

    assert status.is_blacklisted is False
    assert status.blocked_reason is None
