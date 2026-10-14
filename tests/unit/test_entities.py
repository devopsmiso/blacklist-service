from blacklist.domain.entities import normalize_email
from blacklist.domain.exceptions import BlacklistError, EmailAlreadyBlacklistedError


def test_normalize_email_trims_and_lowercases():
    assert normalize_email("  User@Example.COM ") == "user@example.com"


def test_email_already_blacklisted_error_keeps_email():
    error = EmailAlreadyBlacklistedError("user@example.com")

    assert isinstance(error, BlacklistError)
    assert error.email == "user@example.com"
    assert "user@example.com" in str(error)
