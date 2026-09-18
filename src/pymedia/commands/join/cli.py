"""Comando ``join``: cli."""

import typer

from pymedia.commands.join.parameters import JoinParameters
from pymedia.commands.join.service import JoinService
from pymedia.errors import UserError
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    MediaInputListArgument,
    OutputOption,
    OverwriteOption,
)
from pymedia.types import OverwriteMode

join_cli = typer.Typer()


JOIN_HELP = _(
    """\
Concatenate different videos into a single media container.

[bold]Example[/bold]:
  Join videos in the specified order:
    > pymedia join input1.mp4 input2.mp4 input3.mp4 -o output.mp4
"""  # noqa
)


@join_cli.command(
    name="join",
    help=JOIN_HELP,
    rich_help_panel="Video commands",
    no_args_is_help=True,
)
def join(
    media_input_list: MediaInputListArgument,
    media_output: OutputOption,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline de unión de contenedores.

    Args:
        media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        UserError: Si se aportan menos de dos vídeos para unir.
    """
    if len(media_input_list) < 2:
        raise UserError(msg=_("It's required to provide at least 2 videos."))

    Logger.create(debug=debug)
    params = JoinParameters.load(
        overwrite=overwrite,
        media_input_list=media_input_list,
        media_output=media_output,
    )
    JoinService(debug=debug, params=params).start()
