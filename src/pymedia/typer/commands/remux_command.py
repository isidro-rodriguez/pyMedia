"""Comando Typer para la remultiplexión de contenedores."""

import typer

from pymedia.errors import MissingArgumentError, OptionError
from pymedia.locales import _  # noqa
from pymedia.pipeline.remux_pipeline import RemuxPipeline
from pymedia.typer.help import REMUX_HELP
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

remux_typer = typer.Typer()


@remux_typer.command(
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
        OptionError: Si se solicita `fast_start` con un contenedor distinto
            de `.mp4`.
    """
    if media_output is None:
        raise MissingArgumentError(name="media_output")
    if fast_start and media_output.suffix != ".mp4":
        raise OptionError(msg=_("Fast start only works for '.mp4' remux."))

    pipeline = RemuxPipeline(debug=debug)
    pipeline.process_parameters(
        media_input=media_input,
        media_output=media_output,
        overwrite=overwrite,
        fast_start=fast_start,
        regenerate_pts=regenerate_pts,
        sort_tracks=sort_tracks,
    )
    pipeline.process_cmd()
