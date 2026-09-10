"""Comando Typer para iniciar la división de contenedores."""

import typer

from pymedia.typer.help import SPLIT_HELP
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    MediaInputArgument,
    OutputOption,
    OverwriteOption,
    TimestampAtMediaOption,
)
from pymedia.types import OverwriteMode

split_typer = typer.Typer()


@split_typer.command(
    name="split",
    help=SPLIT_HELP,
    rich_help_panel="Video commands",
    no_args_is_help=True,
)
def split(
    media_input: MediaInputArgument,
    timestamp_at: TimestampAtMediaOption,
    output: OutputOption = None,
    overwrite: OverwriteOption = OverwriteMode.YES,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline.

    Args:
        media_input: Ruta del fichero de vídeo a procesar.
        timestamp_at: Lista de marcas de tiempo para dividir el vídeo.
        output: Ruta absoluta del fichero de salida procesado.
        overwrite: Política ante conflicto de salida ya existente.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = SplitPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        timestamp_at=timestamp_at,
        output=output,
        overwrite=overwrite,
    )
    if not pipeline.resolve_overwrite():
        return
    pipeline.process_cmd()
