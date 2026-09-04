"""Comando Typer para mostrar la información de metadatos de un vídeo."""

from pymedia.locales import _  # noqa
from pymedia.pipeline.info_pipeline import InfoPipeline
from pymedia.typer.instance import typer_instance
from pymedia.typer.options import DebugOption, HelpOption, InputSingleArgument

_HELP = _(
    """\
Shows information about a video.

[bold]Example[/bold]:
  Shows video's metadata:   
    > pymedia info input.mp4
"""
)


@typer_instance.command(
    help=_HELP,
    no_args_is_help=True,
)
def info(
    input_single: InputSingleArgument,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline.

    Args:
        input_single: Ruta del fichero de vídeo a procesar.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    pipeline = InfoPipeline(debug=debug)
    pipeline.process_parameters(input_single=input_single)
    pipeline.process_cmd()
