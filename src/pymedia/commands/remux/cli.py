"""Comando ``remux``: cli."""

import typer

from pymedia.commands.remux.parameters import RemuxParameters
from pymedia.commands.remux.service import RemuxService
from pymedia.errors import MissingArgumentError, UserError
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.typer.options import (
    DebugOption,
    FastStartOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    RegeneratePtsOption,
    SortTracksOption,
)
from pymedia.types import OverwriteMode

remux_cli = typer.Typer()


REMUX_HELP = _(
    """\
Change container and metadata without transcoding.

[bold]Examples[/bold]:
  Change video container:
    > pymedia remux input.mp4 -o output.mkv
  Fix faststart moving moov atom at the start 
    > pymedia remux input.mp4 --faststart -o output.mkv 
  Fix broken timestamps
    > pymedia remux input.mp4 --getpts -o output.mkv
  Sort stream tracks
    > pymedia remux input.mp4 --sort-tracks -o output.mp4
"""  # noqa
)


@remux_cli.command(
    name="remux",
    help=REMUX_HELP,
    rich_help_panel="Video commands",
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
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline de `remux`.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        fast_start: Mueve el índice al inicio acelerando su reproducción.
        regenerate_pts: Regenera los marcadores de tiempo corruptos.
        sort_tracks: Ordena las pistas por tipo y luego alfabéticamente por idioma.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        MissingArgumentError: Si no se indica la salida.
        UserError: Si se solicita `fast_start` con un contenedor distinto de `.mp4`.
    """
    if media_output is None:
        raise MissingArgumentError(name="media_output")
    if fast_start and media_output.suffix != ".mp4":
        raise UserError(msg=_("Fast start only works for '.mp4' remux."))

    # Logger.create configura el logger raíz (nivel DEBUG) de forma idempotente;
    # params y service lo recuperan después con Logger.load().
    Logger.create(debug=debug)
    params = RemuxParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        media_output=media_output,
        fast_start=fast_start,
        regenerate_pts=regenerate_pts,
        sort_tracks=sort_tracks,
    )
    RemuxService(debug=debug, params=params).start()
