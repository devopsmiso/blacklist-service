"""Excepciones del dominio."""


class BlacklistError(Exception):
    """Error base del dominio de la lista negra."""


class EmailAlreadyBlacklistedError(BlacklistError):
    """El email ya existe en la lista negra global."""

    def __init__(self, email: str) -> None:
        super().__init__(f"El email '{email}' ya está en la lista negra global.")
        self.email = email
