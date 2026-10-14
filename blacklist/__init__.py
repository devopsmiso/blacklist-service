"""Microservicio de lista negra global de emails.

`create_app` es la raíz de composición: crea la aplicación Flask y conecta
las capas (API -> casos de uso -> repositorio) por inyección de dependencias.
No abre conexiones a la base de datos, así los comandos de consola (por
ejemplo `flask generate-token`) funcionan sin PostgreSQL disponible.
"""
import logging

from flask import Flask
from flask_restful import Api
from werkzeug.middleware.proxy_fix import ProxyFix

from blacklist.api.auth import register_jwt_handlers
from blacklist.api.commands import register_commands
from blacklist.api.error_handlers import register_error_handlers
from blacklist.api.request_logging import register_request_logging
from blacklist.api.routes import register_routes
from blacklist.config import Config
from blacklist.extensions import db, jwt, ma
from blacklist.infrastructure.sqlalchemy_blacklist_repository import (
    SQLAlchemyBlacklistRepository,
)
from blacklist.logging_config import configure_logging
from blacklist.use_cases.add_email_to_blacklist import AddEmailToBlacklist
from blacklist.use_cases.get_blacklist_status import GetBlacklistStatus
from blacklist.version import __version__

logger = logging.getLogger(__name__)


def create_app(config=None) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config or Config())
    configure_logging(app.config["LOG_LEVEL"])

    # IP real del cliente detrás del balanceador (X-Forwarded-For).
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=app.config["PROXY_FIX_X_FOR"])

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    register_jwt_handlers(jwt)
    register_error_handlers(app)
    register_request_logging(app)
    register_commands(app)

    repository = SQLAlchemyBlacklistRepository(db.session)
    register_routes(
        Api(app),
        add_email_use_case=AddEmailToBlacklist(repository),
        get_status_use_case=GetBlacklistStatus(repository),
    )

    logger.info("Microservicio de lista negra iniciado (versión %s)", __version__)
    return app
