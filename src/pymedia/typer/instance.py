"""Instancia de Typer y sus comandos."""

import typer

from pymedia.typer.help import MAIN_HELP
from pymedia.typer.options import HelpOption

typer_instance = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
    add_completion=False,
)


@typer_instance.callback(help=MAIN_HELP)
def main(
    help_: HelpOption = False,  # noqa
) -> None:
    """Muestra la ayuda global de la aplicación cuando se invoca con `--help`.

    Args:
        help_: Solicitud explícita de ayuda del comando.
    """
    pass
