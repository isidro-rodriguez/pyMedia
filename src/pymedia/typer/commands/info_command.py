"""Comando Typer para mostrar la información de metadatos de un vídeo."""

from pymedia.locales import _  # noqa
import typer

from pymedia.pipeline.info_pipeline import InfoPipeline
from pymedia.typer.options import DebugOption, HelpOption, MediaInputArgument

info_typer = typer.Typer()

_HELP = _(
    """\
Shows information about a video.

[bold]Example[/bold]:
  Shows video's metadata:
    > pymedia info input.mp4
"""
)


@info_typer.command(
    name="info",
    help=_HELP,
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
