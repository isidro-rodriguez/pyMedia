"""Comando ``info``: cli."""

import typer

from pymedia.commands.info.parameters import InfoParameters
from pymedia.commands.info.service import InfoService
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.typer.options import DebugOption, HelpOption, MediaInputArgument

info_cli = typer.Typer()


INFO_HELP = _(
    """\
Shows information about a video.

[bold]Example[/bold]:
  Shows video's metadata:
    > pymedia info input.mp4
"""  # noqa
)


@info_cli.command(
    name="info",
    help=INFO_HELP,
    rich_help_panel="Analysis commands",
    no_args_is_help=True,
)
def info(
    media_input: MediaInputArgument,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    Logger.create(debug=debug)
    params = InfoParameters.load(media_input=media_input)
    InfoService(debug=debug, params=params).start()
