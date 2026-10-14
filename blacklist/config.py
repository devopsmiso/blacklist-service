"""Configuración de la aplicación a partir de variables de entorno."""
import os
from urllib.parse import quote_plus


def _require_env(name: str) -> str:
    """Retorna el valor de una variable de entorno obligatoria."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"La variable de entorno '{name}' es obligatoria.")
    return value


def build_database_uri() -> str:
    """Construye la URI de conexión a PostgreSQL (local o AWS RDS)."""
    user = quote_plus(_require_env("DB_USER"))
    password = quote_plus(_require_env("DB_PASSWORD"))
    host = _require_env("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = _require_env("DB_NAME")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


class Config:
    """Configuración de ejecución leída del entorno al instanciarse."""

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {"pool_pre_ping": True}
    # Token estático: los JWT emitidos no expiran (requisito de la entrega).
    JWT_ACCESS_TOKEN_EXPIRES = False
    # Permite que los errores de JWT lleguen a sus manejadores con Flask-RESTful.
    PROPAGATE_EXCEPTIONS = True
    # Respuestas JSON en UTF-8 (sin escapar tildes).
    JSON_AS_ASCII = False
    RESTFUL_JSON = {"ensure_ascii": False}

    def __init__(self) -> None:
        self.SQLALCHEMY_DATABASE_URI = build_database_uri()
        self.JWT_SECRET_KEY = _require_env("JWT_SECRET_KEY")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        # Número de proxies de confianza delante de la app (X-Forwarded-For).
        self.PROXY_FIX_X_FOR = int(os.getenv("PROXY_FIX_X_FOR", "1"))
