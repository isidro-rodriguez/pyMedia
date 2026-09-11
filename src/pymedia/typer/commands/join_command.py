"""Comando Typer para iniciar la unión de contenedores."""

import typer

from pymedia.errors import OptionError
from pymedia.locales import _  # noqa
from pymedia.pipeline.join_pipeline import JoinPipeline
from pymedia.typer.help import JOIN_HELP
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    MediaInputListArgument,
    OutputOption,
    OverwriteOption,
)
from pymedia.types import OverwriteMode

join_typer = typer.Typer()


@join_typer.command(
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
    """
    if len(media_input_list) < 2:
        raise OptionError(msg=_("It's required to provide at least 2 videos."))

    pipeline = JoinPipeline(debug=debug)
    pipeline.process_parameters(
        media_input_list=media_input_list,
        media_output=media_output,
        overwrite=overwrite,
    )
    pipeline.process_cmd()
