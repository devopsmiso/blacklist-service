"""Caso de uso: consultar si un email está en la lista negra global."""
import logging
from dataclasses import dataclass
from typing import Optional

from blacklist.domain.entities import normalize_email
from blacklist.domain.repository import BlacklistRepository

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BlacklistStatus:
    """Resultado de la consulta."""

    email: str
    is_blacklisted: bool
    blocked_reason: Optional[str]


class GetBlacklistStatus:
    def __init__(self, repository: BlacklistRepository) -> None:
        self._repository = repository

    def execute(self, email: str) -> BlacklistStatus:
        normalized = normalize_email(email)
        entry = self._repository.find_by_email(normalized)
        status = BlacklistStatus(
            email=normalized,
            is_blacklisted=entry is not None,
            blocked_reason=entry.blocked_reason if entry else None,
        )
        logger.info("Consulta de lista negra (encontrado=%s)", status.is_blacklisted)
        return status
