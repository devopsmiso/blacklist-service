from blacklist.use_cases.get_blacklist_status import GetBlacklistStatus
from blacklist.version import __version__


def test_health_returns_ok_and_version_without_token(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "version": __version__}


def test_unknown_route_returns_json_404(client):
    response = client.get("/no-existe")

    assert response.status_code == 404
    assert "message" in response.get_json()


def test_unsupported_method_returns_405(client, auth_headers):
    response = client.delete("/blacklists", headers=auth_headers)

    assert response.status_code == 405
    assert "message" in response.get_json()


def test_unexpected_error_returns_500_without_details(client, auth_headers, monkeypatch):
    def broken_execute(self, email):
        raise RuntimeError("detalle interno")

    monkeypatch.setattr(GetBlacklistStatus, "execute", broken_execute)

    response = client.get("/blacklists/a@b.com", headers=auth_headers)

    assert response.status_code == 500
    assert response.get_json() == {"message": "Error interno del servidor."}
