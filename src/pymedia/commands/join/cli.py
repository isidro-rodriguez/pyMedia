"""Comando ``join``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    DebugOption,
    HelpOption,
    MediaInputListArgument,
    OutputOption,
    OverwriteOption,
    ShowCmdOption,
    StripMetadataOption,
)
from pymedia.commands.join.parameters import JoinParameters
from pymedia.commands.join.service import JoinService
from pymedia.errors import UserError
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

join_cli = typer.Typer()


JOIN_HELP = _(
    """\
Concatenate different compatible videos into a single media container.

Compatible videos must have same codecs, dimensions, tracks, ...

[bold]Example[/bold]:
  Join videos in the specified order:
    > pymedia join input1.mp4 input2.mp4 input3.mp4 -o output.mp4
"""
)


@join_cli.command(
    name="join",
    help=JOIN_HELP,
    rich_help_panel=_("Video commands"),
    no_args_is_help=True,
)
def join(
    media_input_list: MediaInputListArgument,
    media_output: OutputOption,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    strip_metadata: StripMetadataOption = False,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``join``.

    Args:
        media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        strip_metadata: No copiar los metadatos del fichero de entrada.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
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
        strip_metadata=strip_metadata,
    )
    JoinService(debug=debug, show_cmd=show_cmd, params=params).start()
