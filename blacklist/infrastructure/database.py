"""Inicialización del esquema de base de datos."""
import logging

from flask import Flask
from sqlalchemy.exc import SQLAlchemyError

from blacklist.extensions import db

logger = logging.getLogger(__name__)


def init_db(app: Flask) -> None:
    """Crea las tablas si no existen.

    Se reintenta una vez porque varias instancias o workers pueden intentar
    crear la tabla al mismo tiempo durante un despliegue en Beanstalk.
    """
    with app.app_context():
        try:
            db.create_all()
        except SQLAlchemyError:
            logger.warning("Falló la creación del esquema, reintentando una vez")
            db.create_all()
    logger.info("Esquema de base de datos verificado")
