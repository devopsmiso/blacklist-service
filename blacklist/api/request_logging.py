"""Log de cada solicitud HTTP atendida."""
import logging

from flask import Flask, request

logger = logging.getLogger("blacklist.access")


def register_request_logging(app: Flask) -> None:
    @app.after_request
    def log_request(response):
        # Se registra la ruta (plantilla) y no la URL para no exponer emails.
        route = request.url_rule.rule if request.url_rule else request.path
        logger.info(
            "%s %s -> %s (ip=%s)",
            request.method,
            route,
            response.status_code,
            request.remote_addr,
        )
        return response
