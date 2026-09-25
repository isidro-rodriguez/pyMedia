"""Comando ``info``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    DebugOption,
    HelpOption,
    MediaInputArgument,
)
from pymedia.commands.info.parameters import InfoParameters
from pymedia.commands.info.service import InfoService
from pymedia.locales import translate as _
from pymedia.logger import Logger

info_cli = typer.Typer()


INFO_HELP = _(
    """\
Shows information about a video.

[bold]Example[/bold]:
  Shows video's metadata:
    > pymedia info input.mp4
"""
)


@info_cli.command(
    name="info",
    help=INFO_HELP,
    rich_help_panel=_("Analysis commands"),
    no_args_is_help=True,
)
def info(
    media_input: MediaInputArgument,
    debug: DebugOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``info``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    Logger.create(debug=debug)
    params = InfoParameters.load(media_input=media_input)
    InfoService(params=params).start()
