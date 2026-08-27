"""Autodescubrimiento y registro de subcomandos."""

import importlib
import inspect
import pkgutil

import typer

from pymedia.commands.base_command import BaseCommand


def register_all(app: typer.Typer) -> None:
    """Descubre todas las subclases de BaseCommand y las registra en la app."""
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module_name}")
    pending: list[type[BaseCommand]] = list(BaseCommand.__subclasses__())
    while pending:
        command_cls = pending.pop()
        pending.extend(command_cls.__subclasses__())
        if not inspect.isabstract(command_cls):
            command_cls.register(app)
