import pytest

ENDPOINTS = [
    ("post", "/blacklists"),
    ("get", "/blacklists/cliente@example.com"),
]


@pytest.mark.parametrize("method, url", ENDPOINTS)
def test_missing_token_returns_401(client, method, url):
    response = getattr(client, method)(url)

    assert response.status_code == 401
    assert response.get_json() == {"message": "Token de autorización requerido."}
    assert "autorización".encode("utf-8") in response.data


@pytest.mark.parametrize("method, url", ENDPOINTS)
def test_non_bearer_header_returns_401(client, method, url):
    response = getattr(client, method)(url, headers={"Authorization": "Token abc"})

    assert response.status_code == 401
    assert response.get_json() == {"message": "Token de autorización requerido."}


@pytest.mark.parametrize("method, url", ENDPOINTS)
def test_invalid_token_returns_401(client, method, url):
    response = getattr(client, method)(
        url, headers={"Authorization": "Bearer token-invalido"}
    )

    assert response.status_code == 401
    assert response.get_json() == {"message": "Token de autorización inválido."}


def test_token_signed_with_other_secret_returns_401(client):
    forged = (
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9."
        "eyJzdWIiOiJ4In0."
        "rXuGq5V1G9nQe2H4l0M8yJmK7JwqQm5n4E0x1Yz2Ab8"
    )

    response = client.get(
        "/blacklists/a@b.com", headers={"Authorization": f"Bearer {forged}"}
    )

    assert response.status_code == 401
