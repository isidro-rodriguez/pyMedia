"""Comando Typer para mostrar la información de metadatos de un vídeo."""

import typer

from pymedia.pipeline.info_pipeline import InfoPipeline
from pymedia.typer.help import INFO_HELP
from pymedia.typer.options import DebugOption, HelpOption, MediaInputArgument

info_typer = typer.Typer()


@info_typer.command(
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
    pipeline = InfoPipeline(debug=debug)
    pipeline.process_parameters(media_input=media_input)
    pipeline.process_cmd()
