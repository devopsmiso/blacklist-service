"""Respuestas uniformes (401) para los errores del Bearer Token."""
from flask import jsonify
from flask_jwt_extended import JWTManager


def register_jwt_handlers(jwt: JWTManager) -> None:
    @jwt.unauthorized_loader
    def missing_token(reason: str):
        return jsonify(message="Token de autorización requerido."), 401

    @jwt.invalid_token_loader
    def invalid_token(reason: str):
        return jsonify(message="Token de autorización inválido."), 401
