"""Comando ``cut``: cli."""

import typer

from pymedia.commands.cut.parameters import CutParameters
from pymedia.commands.cut.service import CutService
from pymedia.errors import MissingRequiredOptionsError, UserError
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    TimestampAtMediaOption,
    TimestampEndMediaOption,
    TimestampStartMediaOption,
)
from pymedia.types import OverwriteMode

cut_cli = typer.Typer()


CUT_HELP = _(
    """\
Cut off a video container's section or split it between different media files.

[bold]Examples[/bold]:
  Cut a section the start of a media file at specific timestamp:
    > pymedia cut input.mp4 --start 00:30
  Cut a section the start and the end of a media file at specifics timestamps:
    > pymedia cut input.mp4 --start 01:00 --end 1:30:00
  Split a media file at specific timestamps:
    > pymedia cut input.mp4 --at 10:05,40:30,1:20:00
"""  # noqa
)


@cut_cli.command(
    name="cut",
    help=CUT_HELP,
    rich_help_panel="Video commands",
    no_args_is_help=True,
)
def cut(
    media_input: MediaInputArgument,
    timestamp_at: TimestampAtMediaOption = None,
    timestamp_start: TimestampStartMediaOption = None,
    timestamp_end: TimestampEndMediaOption = None,
    media_output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        timestamp_at: Lista de marcas de tiempo para dividir el vídeo.
        timestamp_start: Indica cuando empieza el vídeo de salida.
        timestamp_end: Indica cuando termina el vídeo de salida.
        media_output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.

    Raises:
        MissingRequiredOptionsError: Si no se indica ninguna marca de tiempo.
        UserError: Si se combinan opciones ambiguas (`--at` con `--start`/`--end`).
    """
    if timestamp_at is None and timestamp_start is None and timestamp_end is None:
        raise MissingRequiredOptionsError(options=["at", "start", "end"])

    if timestamp_at is not None and (
        timestamp_start is not None or timestamp_end is not None
    ):
        raise UserError(
            msg=_("Ambiguous options: You can't select --at with --start or --end.")
        )

    Logger.create(debug=debug)
    params = CutParameters.load(
        overwrite=overwrite,
        media_input=media_input,
        timestamp_at=timestamp_at,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        media_output=media_output,
    )
    CutService(debug=debug, params=params).start()
