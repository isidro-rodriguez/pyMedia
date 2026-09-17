"""Instancia de Typer y sus comandos."""

import typer

from pymedia.typer.help import MAIN_HELP
from pymedia.typer.options import DebugOption, HelpOption, VersionOption

typer_instance = typer.Typer(
    name="pyMedia",
    rich_markup_mode="rich",
    no_args_is_help=True,
)


@typer_instance.callback(help=MAIN_HELP)
def main(
    help_: HelpOption = False,  # noqa
    debug: DebugOption = False,  # noqa
    version: VersionOption = False,  # noqa
) -> None:
    """Muestra la ayuda global de la aplicación cuando se invoca con `--help`.

    Args:
        help_: Solicitud explícita de ayuda del comando.
        debug: Nota informativa para avisar que se puede utilizar modo DEBUG.
        version: Mostrar la versión de la aplicación.
    """
    pass
