"""Recursos REST. Solo traducen HTTP <-> casos de uso."""
from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource

from blacklist.api.schemas import (
    AddEmailRequestSchema,
    AddEmailResponseSchema,
    BlacklistStatusSchema,
)
from blacklist.use_cases.add_email_to_blacklist import (
    AddEmailCommand,
    AddEmailToBlacklist,
)
from blacklist.use_cases.get_blacklist_status import GetBlacklistStatus
from blacklist.version import __version__

add_email_request_schema = AddEmailRequestSchema()
add_email_response_schema = AddEmailResponseSchema()
blacklist_status_schema = BlacklistStatusSchema()


class BlacklistCollectionResource(Resource):
    """POST /blacklists"""

    method_decorators = [jwt_required()]

    def __init__(self, add_email_use_case: AddEmailToBlacklist) -> None:
        self._add_email = add_email_use_case

    def post(self):
        data = add_email_request_schema.load(request.get_json(silent=True) or {})
        entry = self._add_email.execute(
            AddEmailCommand(
                email=data["email"],
                app_uuid=str(data["app_uuid"]),
                blocked_reason=data["blocked_reason"],
                ip_address=request.remote_addr,
            )
        )
        response = {
            "message": "El email fue agregado a la lista negra global.",
            "id": entry.id,
            "email": entry.email,
            "created_at": entry.created_at,
        }
        return add_email_response_schema.dump(response), 201


class BlacklistItemResource(Resource):
    """GET /blacklists/<string:email>"""

    method_decorators = [jwt_required()]

    def __init__(self, get_status_use_case: GetBlacklistStatus) -> None:
        self._get_status = get_status_use_case

    def get(self, email: str):
        status = self._get_status.execute(email)
        return blacklist_status_schema.dump(status), 200


class HealthResource(Resource):
    """GET /health — usado por los health checks de AWS Beanstalk.

    Incluye la versión para validar qué versión atiende cada instancia
    durante las estrategias de despliegue.
    """

    def get(self):
        return {"status": "ok", "version": __version__}, 200
