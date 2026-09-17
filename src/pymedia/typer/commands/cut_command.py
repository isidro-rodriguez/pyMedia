"""Comando Typer para iniciar el corte de contenedores."""

import typer

from pymedia.errors import MissingRequiredOptionsError, UserError
from pymedia.locales import _  # noqa
from pymedia.pipeline.cut_pipeline import CutPipeline
from pymedia.typer.help import CUT_HELP
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

cut_typer = typer.Typer()


@cut_typer.command(
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
        MissingArgumentError: Si no se indica la lista de marcas de tiempo.
    """
    if timestamp_at is None and timestamp_start is None and timestamp_end is None:
        raise MissingRequiredOptionsError(options=["at", "start", "end"])

    if timestamp_at is not None and (
        timestamp_start is not None or timestamp_end is not None
    ):
        raise UserError(
            msg=_("Ambiguous options: You can't select --at with --start or --end.")
        )

    pipeline = CutPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        timestamp_at=timestamp_at,
        timestamp_start=timestamp_start,
        timestamp_end=timestamp_end,
        media_output=media_output,
        overwrite=overwrite,
    )
    pipeline.process_cmd()
