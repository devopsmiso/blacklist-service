"""Traducción de excepciones a respuestas JSON."""
import logging

from flask import Flask, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from blacklist.domain.exceptions import EmailAlreadyBlacklistedError

logger = logging.getLogger(__name__)


def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        logger.info("Solicitud rechazada por datos inválidos: %s", error.messages)
        return jsonify(message="Datos de entrada inválidos.", errors=error.messages), 400

    @app.errorhandler(EmailAlreadyBlacklistedError)
    def handle_duplicate_email(error: EmailAlreadyBlacklistedError):
        return jsonify(message="El email ya se encuentra en la lista negra global."), 409

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return jsonify(message=error.description), error.code

    @app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        logger.exception("Error inesperado procesando la solicitud")
        return jsonify(message="Error interno del servidor."), 500
