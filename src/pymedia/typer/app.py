"""Instancia de Typer y sus comandos."""

import typer

from pymedia.typer.options import (
    HelpOption,
)

app = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main(
    help_: HelpOption = False,  # noqa
) -> None:
    """Muestra la ayuda global de la aplicación cuando se invoca con `--help`."""
    pass
