"""Contrato de persistencia (inversión de dependencias)."""
from abc import ABC, abstractmethod
from typing import Optional

from blacklist.domain.entities import BlacklistEntry


class BlacklistRepository(ABC):
    """Puerto que los casos de uso usan para persistir la lista negra."""

    @abstractmethod
    def add(self, entry: BlacklistEntry) -> BlacklistEntry:
        """Guarda la entrada y la retorna con su identificador asignado."""

    @abstractmethod
    def find_by_email(self, email: str) -> Optional[BlacklistEntry]:
        """Retorna la entrada del email normalizado o None si no existe."""
