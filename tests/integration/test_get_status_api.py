def test_get_returns_true_and_reason_for_blacklisted_email(client, auth_headers, valid_payload):
    client.post("/blacklists", json=valid_payload, headers=auth_headers)

    response = client.get("/blacklists/CLIENTE@example.com", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {
        "email": "cliente@example.com",
        "is_blacklisted": True,
        "blocked_reason": "Solicitud del cliente",
    }


def test_get_returns_false_for_unknown_email(client, auth_headers):
    response = client.get("/blacklists/nadie@example.com", headers=auth_headers)

    assert response.status_code == 200
    assert response.get_json() == {
        "email": "nadie@example.com",
        "is_blacklisted": False,
        "blocked_reason": None,
    }
