"""Punto de entrada WSGI.

AWS Elastic Beanstalk (plataforma Python) busca por defecto el objeto
`application` en el módulo `application.py`. Al arrancar se verifica el
esquema de la base de datos (crea la tabla si no existe).
"""
import os

from blacklist import create_app
from blacklist.infrastructure.database import init_db

application = create_app()
init_db(application)

if __name__ == "__main__":
    # Solo para desarrollo local. En Docker y Beanstalk se usa gunicorn.
    application.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
