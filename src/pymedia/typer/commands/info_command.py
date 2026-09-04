"""Comando Typer para mostrar la información de metadatos de un vídeo."""

import typer

from pymedia.locales import _  # noqa
from pymedia.pipeline.info_pipeline import InfoPipeline
from pymedia.typer.options import DebugOption, HelpOption, InputSingleArgument

_HELP = _(
    """\
Shows information about a video.

[bold]Example[/bold]:
  Shows video's metadata:
    > pymedia info input.mp4
"""
)

info_command = typer.Typer(
    name="info",
    help=_HELP,
    no_args_is_help=True,
)


@info_command.callback(invoke_without_command=True)
def _info_run(
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


if __name__ == "__main__":
    info_command()
