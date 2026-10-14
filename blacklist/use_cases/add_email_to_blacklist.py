"""Caso de uso: agregar un email a la lista negra global."""
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Optional

from blacklist.domain.entities import BlacklistEntry, normalize_email
from blacklist.domain.exceptions import EmailAlreadyBlacklistedError
from blacklist.domain.repository import BlacklistRepository

logger = logging.getLogger(__name__)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class AddEmailCommand:
    """Datos de entrada del caso de uso."""

    email: str
    app_uuid: str
    blocked_reason: Optional[str]
    ip_address: str


class AddEmailToBlacklist:
    def __init__(
        self,
        repository: BlacklistRepository,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._repository = repository
        self._clock = clock

    def execute(self, command: AddEmailCommand) -> BlacklistEntry:
        email = normalize_email(command.email)
        if self._repository.find_by_email(email) is not None:
            logger.warning(
                "Email duplicado rechazado (app_uuid=%s, ip=%s)",
                command.app_uuid,
                command.ip_address,
            )
            raise EmailAlreadyBlacklistedError(email)

        entry = BlacklistEntry(
            email=email,
            app_uuid=command.app_uuid,
            blocked_reason=command.blocked_reason,
            ip_address=command.ip_address,
            created_at=self._clock(),
        )
        saved = self._repository.add(entry)
        logger.info(
            "Email agregado a la lista negra (id=%s, app_uuid=%s, ip=%s)",
            saved.id,
            saved.app_uuid,
            saved.ip_address,
        )
        return saved
