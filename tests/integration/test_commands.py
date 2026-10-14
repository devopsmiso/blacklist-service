from flask_jwt_extended import decode_token


def test_generate_token_command_returns_non_expiring_valid_jwt(app, client):
    result = app.test_cli_runner().invoke(args=["generate-token"])
    token = result.output.strip()

    assert result.exit_code == 0
    with app.app_context():
        claims = decode_token(token)
    assert claims["sub"] == "blacklist-client"
    assert "exp" not in claims

    response = client.get(
        "/blacklists/a@b.com", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


def test_generate_token_command_accepts_identity(app):
    result = app.test_cli_runner().invoke(args=["generate-token", "--identity", "app-x"])

    with app.app_context():
        assert decode_token(result.output.strip())["sub"] == "app-x"
