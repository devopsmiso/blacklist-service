"""Instancias únicas de las extensiones de Flask."""
import warnings

from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

# Flask-Marshmallow advierte que falta marshmallow-sqlalchemy; no se usa
# porque los esquemas se definen explícitamente, así que se silencia.
with warnings.catch_warnings():
    warnings.filterwarnings(
        "ignore",
        message="Flask-SQLAlchemy integration requires marshmallow-sqlalchemy",
        category=UserWarning,
    )
    from flask_marshmallow import Marshmallow

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
