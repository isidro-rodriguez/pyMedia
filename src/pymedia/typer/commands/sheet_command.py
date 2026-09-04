"""Comando Typer para mostrar la información de metadatos de un vídeo."""

from pymedia.data.types import OverwriteMode, PresetsSheetMode
from pymedia.locales import _  # noqa
from pymedia.pipeline.sheet_pipeline import SheetPipeline
from pymedia.typer.instance import (
    typer_instance,
)
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    InputListArgument,
    OutputDirectoryOption,
    OutputOption,
    OverwriteOption,
    PresetSheetOption,
)
from pymedia.typer.service import validate_conflict_output_options

_HELP = _(
    """\
Generates a thumbnail grid sheet with media info header.

[bold]Examples[/bold]:
  Generate a vcs with default HD preset:   
    > pymedia sheet input.mp4
  Generates a vcs with different preset and specified output:
    > pymedia sheet input.mp4 --preset fhd -o vcs.webp
"""
)


@typer_instance.command(
    help=_HELP,
    no_args_is_help=True,
)
def sheet(
    input_list: InputListArgument,
    output: OutputOption = None,
    output_directory: OutputDirectoryOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    preset_sheet: PresetSheetOption = PresetsSheetMode.HD,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline.

    Args:
        input_list: Lista de rutas de los ficheros de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        output_directory: Directorio de salida para lotes de ficheros.
        overwrite: Política ante conflicto de salida ya existente.
        preset_sheet: Estilo de hoja preajustado.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    validate_conflict_output_options(
        input_list=input_list, output=output, output_directory=output_directory
    )
    for input_single in input_list:
        pipeline = SheetPipeline(debug=debug)
        pipeline.process_parameters(
            input_single=input_single,
            output=output,
            output_directory=output_directory,
            overwrite=overwrite,
            preset_sheet=preset_sheet,
        )
        if not pipeline.resolve_overwrite():
            continue
        pipeline.process_cmd()
