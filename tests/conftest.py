import pytest
from flask_jwt_extended import create_access_token

from blacklist import create_app
from blacklist.config import Config
from blacklist.extensions import db
from blacklist.infrastructure.database import init_db

VALID_APP_UUID = "9f1c3a52-7d4b-4c1e-9a3f-2b8e6d0c1a77"


class TestingConfig(Config):
    """Hereda la configuración real; solo cambia la base de datos y secretos."""

    TESTING = True

    def __init__(self) -> None:  # No lee variables de entorno.
        self.SQLALCHEMY_DATABASE_URI = "sqlite://"
        self.JWT_SECRET_KEY = "test-secret-key"
        self.LOG_LEVEL = "DEBUG"
        self.PROXY_FIX_X_FOR = 1


@pytest.fixture
def app():
    app = create_app(TestingConfig())
    init_db(app)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(app):
    with app.app_context():
        token = create_access_token(identity="test-client")
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def valid_payload():
    return {
        "email": "Cliente@Example.com",
        "app_uuid": VALID_APP_UUID,
        "blocked_reason": "Solicitud del cliente",
    }
