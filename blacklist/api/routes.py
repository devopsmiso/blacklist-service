"""Registro de rutas del API (contrato definido en la Entrega 1)."""
from flask_restful import Api

from blacklist.api.resources import (
    BlacklistCollectionResource,
    BlacklistItemResource,
    HealthResource,
)
from blacklist.use_cases.add_email_to_blacklist import AddEmailToBlacklist
from blacklist.use_cases.get_blacklist_status import GetBlacklistStatus


def register_routes(
    api: Api,
    add_email_use_case: AddEmailToBlacklist,
    get_status_use_case: GetBlacklistStatus,
) -> None:
    api.add_resource(
        BlacklistCollectionResource,
        "/blacklists",
        resource_class_kwargs={"add_email_use_case": add_email_use_case},
    )
    api.add_resource(
        BlacklistItemResource,
        "/blacklists/<string:email>",
        resource_class_kwargs={"get_status_use_case": get_status_use_case},
    )
    api.add_resource(HealthResource, "/health")
