import pytest

from blacklist.extensions import db
from blacklist.infrastructure.models import BlacklistModel


def _stored(app, email):
    with app.app_context():
        return db.session.query(BlacklistModel).filter_by(email=email).one()


def test_post_adds_email_and_stores_ip_and_timestamp(app, client, auth_headers, valid_payload):
    response = client.post(
        "/blacklists",
        json=valid_payload,
        headers={**auth_headers, "X-Forwarded-For": "181.49.12.7"},
    )

    body = response.get_json()
    assert response.status_code == 201
    assert body["message"] == "El email fue agregado a la lista negra global."
    assert body["email"] == "cliente@example.com"
    assert body["id"] == 1
    assert body["created_at"]

    stored = _stored(app, "cliente@example.com")
    assert stored.ip_address == "181.49.12.7"
    assert stored.app_uuid == valid_payload["app_uuid"]
    assert stored.blocked_reason == "Solicitud del cliente"
    assert stored.created_at is not None


def test_post_uses_remote_address_without_proxy_header(app, client, auth_headers, valid_payload):
    client.post("/blacklists", json=valid_payload, headers=auth_headers)

    assert _stored(app, "cliente@example.com").ip_address == "127.0.0.1"


def test_post_blocked_reason_is_optional(app, client, auth_headers, valid_payload):
    del valid_payload["blocked_reason"]

    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)

    assert response.status_code == 201
    assert _stored(app, "cliente@example.com").blocked_reason is None


def test_post_duplicate_email_returns_409(client, auth_headers, valid_payload):
    client.post("/blacklists", json=valid_payload, headers=auth_headers)
    valid_payload["email"] = "CLIENTE@example.com"

    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)

    assert response.status_code == 409
    assert response.get_json() == {
        "message": "El email ya se encuentra en la lista negra global."
    }


@pytest.mark.parametrize(
    "changes, field",
    [
        ({"email": "no-es-un-email"}, "email"),
        ({"email": None}, "email"),
        ({"email": "a" * 244 + "@example.com"}, "email"),
        ({"app_uuid": "123"}, "app_uuid"),
        ({"blocked_reason": "x" * 256}, "blocked_reason"),
        ({"campo_extra": "valor"}, "campo_extra"),
    ],
)
def test_post_invalid_data_returns_400(client, auth_headers, valid_payload, changes, field):
    response = client.post(
        "/blacklists", json={**valid_payload, **changes}, headers=auth_headers
    )

    body = response.get_json()
    assert response.status_code == 400
    assert body["message"] == "Datos de entrada inválidos."
    assert field in body["errors"]


def test_post_without_body_reports_required_fields(client, auth_headers):
    response = client.post("/blacklists", headers=auth_headers)

    errors = response.get_json()["errors"]
    assert response.status_code == 400
    assert set(errors) == {"email", "app_uuid"}


def test_post_accepts_255_character_reason(client, auth_headers, valid_payload):
    valid_payload["blocked_reason"] = "x" * 255

    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)

    assert response.status_code == 201


def test_post_accepts_255_character_email(client, auth_headers, valid_payload):
    valid_payload["email"] = "a" * 243 + "@example.com"

    response = client.post("/blacklists", json=valid_payload, headers=auth_headers)

    assert response.status_code == 201
