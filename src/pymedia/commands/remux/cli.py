"""Comando ``remux``: cli."""

import typer

from pymedia.commands.base_cli_options import (
    DebugOption,
    FastStartOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    RegeneratePtsOption,
    ShowCmdOption,
    SortTracksOption,
)
from pymedia.commands.remux.parameters import RemuxParameters
from pymedia.commands.remux.service import RemuxService
from pymedia.errors import MissingArgumentError, UserError
from pymedia.locales import _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode

remux_cli = typer.Typer()


REMUX_HELP = _(
    """\
Change container and metadata without transcoding.

[bold]Examples[/bold]:
  Change video container:
    > pymedia remux input.mp4 -o output.mkv
  Fix faststart moving moov atom at the start
    > pymedia remux input.mp4 --fast-start -o output.mp4
  Fix broken timestamps
    > pymedia remux input.mp4 --genpts -o output.mkv
  Sort stream tracks
    > pymedia remux input.mp4 --sort-tracks -o output.mp4
"""
)


@remux_cli.command(
    name="remux",
    help=REMUX_HELP,
    rich_help_panel=_("Video commands"),
    no_args_is_help=True,
)
def remux(
    media_input: MediaInputArgument,
    media_output: OutputOption,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    fast_start: FastStartOption = False,
    regenerate_pts: RegeneratePtsOption = False,
    sort_tracks: SortTracksOption = False,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``remux``.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        fast_start: Mueve el índice al inicio acelerando su reproducción.
        regenerate_pts: Regenera los marcadores de tiempo corruptos.
        sort_tracks: Ordena las pistas por tipo y luego alfabéticamente por idioma.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        MissingArgumentError: Si no se indica la salida.
        UserError: Si se solicita `fast_start` con un contenedor distinto de `.mp4`.
    """
    if media_output is None:
        raise MissingArgumentError(name="media_output")
    if fast_start and media_output.suffix != ".mp4":
        raise UserError(msg=_("Fast start only works for '.mp4' remux."))

    Logger.create(debug=debug)
    params = RemuxParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        media_output=media_output,
        fast_start=fast_start,
        regenerate_pts=regenerate_pts,
        sort_tracks=sort_tracks,
    )
    RemuxService(debug=debug, show_cmd=show_cmd, params=params).start()
