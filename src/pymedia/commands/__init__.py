"""Autodescubrimiento y registro de subcomandos."""

import importlib
import pkgutil

import typer

from pymedia.commands.command import Command


def register_all(app: typer.Typer) -> None:
    """Descubre todas las subclases de Command y las registra en la app."""
    package = __name__
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{package}.{module_name}")

    for command_cls in Command.__subclasses__():
        command_cls.register(app)
