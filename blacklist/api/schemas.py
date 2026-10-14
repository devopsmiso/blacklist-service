"""Esquemas Marshmallow de validación y serialización."""
from marshmallow import fields, validate

from blacklist.extensions import ma


class AddEmailRequestSchema(ma.Schema):
    """Cuerpo de POST /blacklists. Rechaza campos no definidos en el contrato."""

    # Mismo límite que la columna `email` (VARCHAR(255)).
    email = fields.Email(required=True, validate=validate.Length(max=255))
    app_uuid = fields.UUID(required=True)
    blocked_reason = fields.String(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=255),
    )


class AddEmailResponseSchema(ma.Schema):
    """Respuesta de POST /blacklists."""

    message = fields.String()
    id = fields.Integer()
    email = fields.String()
    created_at = fields.DateTime()


class BlacklistStatusSchema(ma.Schema):
    """Respuesta de GET /blacklists/<email>."""

    email = fields.String()
    is_blacklisted = fields.Boolean()
    blocked_reason = fields.String(allow_none=True)
