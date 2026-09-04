"""Instancia de Typer y sus comandos."""

import typer

from pymedia.locales import _  # noqa
from pymedia.typer.options import HelpOption

typer_instance = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


@typer_instance.callback()
def main(
    help_: HelpOption = False,  # noqa
) -> None:
    """Muestra la ayuda global de la aplicación cuando se invoca con `--help`."""
    pass
