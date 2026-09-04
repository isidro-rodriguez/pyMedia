"""Autodescubrimiento y registro de subcomandos."""

import importlib
import inspect
import pkgutil

import typer

from pymedia.pipeline.base_pipeline import BasePipeline


def register_all(app: typer.Typer) -> None:
    """Descubre todas las subclases de BasePipeline y las registra en la typer_instance.

    Args:
        app: Instancia de la aplicación Typer donde se registran los comandos.
    """
    for _, module_name, _ in pkgutil.iter_modules(__path__):
        importlib.import_module(f"{__name__}.{module_name}")
    pending: list[type[BasePipeline]] = list(BasePipeline.__subclasses__())
    while pending:
        command_cls = pending.pop()
        pending.extend(command_cls.__subclasses__())
        if not inspect.isabstract(command_cls):
            command_cls.register(app)
