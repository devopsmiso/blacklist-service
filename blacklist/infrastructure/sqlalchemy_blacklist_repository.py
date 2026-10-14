"""Implementación del repositorio de la lista negra con SQLAlchemy."""
from typing import Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from blacklist.domain.entities import BlacklistEntry
from blacklist.domain.exceptions import EmailAlreadyBlacklistedError
from blacklist.domain.repository import BlacklistRepository
from blacklist.infrastructure.models import BlacklistModel


class SQLAlchemyBlacklistRepository(BlacklistRepository):
    def __init__(self, session) -> None:
        self._session = session

    def add(self, entry: BlacklistEntry) -> BlacklistEntry:
        model = BlacklistModel(
            email=entry.email,
            app_uuid=entry.app_uuid,
            blocked_reason=entry.blocked_reason,
            ip_address=entry.ip_address,
            created_at=entry.created_at,
        )
        self._session.add(model)
        try:
            self._session.commit()
        except IntegrityError as error:
            # Carrera entre solicitudes concurrentes con el mismo email.
            self._session.rollback()
            raise EmailAlreadyBlacklistedError(entry.email) from error
        except SQLAlchemyError:
            self._session.rollback()
            raise
        return self._to_entity(model)

    def find_by_email(self, email: str) -> Optional[BlacklistEntry]:
        model = (
            self._session.query(BlacklistModel).filter_by(email=email).one_or_none()
        )
        return self._to_entity(model) if model else None

    @staticmethod
    def _to_entity(model: BlacklistModel) -> BlacklistEntry:
        return BlacklistEntry(
            id=model.id,
            email=model.email,
            app_uuid=model.app_uuid,
            blocked_reason=model.blocked_reason,
            ip_address=model.ip_address,
            created_at=model.created_at,
        )
