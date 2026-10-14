"""Entidades del dominio de la lista negra global."""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


def normalize_email(email: str) -> str:
    """Normaliza el email para que la búsqueda no dependa de mayúsculas."""
    return email.strip().lower()


@dataclass(frozen=True)
class BlacklistEntry:
    """Email agregado a la lista negra global."""

    email: str
    app_uuid: str
    blocked_reason: Optional[str]
    ip_address: str
    created_at: datetime
    id: Optional[int] = None
