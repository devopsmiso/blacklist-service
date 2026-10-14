"""Comandos de consola de Flask."""
import click
from flask import Flask
from flask_jwt_extended import create_access_token


def register_commands(app: Flask) -> None:
    @app.cli.command("generate-token")
    @click.option("--identity", default="blacklist-client", show_default=True)
    def generate_token(identity: str) -> None:
        """Genera el Bearer Token estático (sin expiración) para consumir el API."""
        click.echo(create_access_token(identity=identity))
