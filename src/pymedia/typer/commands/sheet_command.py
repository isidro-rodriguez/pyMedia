"""Comando Typer para mostrar la información de metadatos de un vídeo."""

import typer

from pymedia.pipeline.sheet_pipeline import SheetPipeline
from pymedia.typer.help import SHEET_HELP
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    MediaInputListArgument,
    OutputDirectoryOption,
    OutputOption,
    OverwriteOption,
    PresetSheetOption,
)
from pymedia.typer.service import validate_conflict_output_options
from pymedia.types import OverwriteMode, PresetsSheetMode

sheet_typer = typer.Typer()


@sheet_typer.command(
    name="sheet",
    help=SHEET_HELP,
    rich_help_panel="Analysis commands",
    no_args_is_help=True,
)
def sheet(
    media_input_list: MediaInputListArgument,
    output: OutputOption = None,
    output_directory: OutputDirectoryOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    preset_sheet: PresetSheetOption = PresetsSheetMode.HD,
    debug: DebugOption = False,
    help_: HelpOption = False,  # noqa
) -> None:
    """Punto de entrada y desarrollo del pipeline.

    Args:
        media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        output_directory: Directorio de salida para lotes de ficheros.
        overwrite: Política ante conflicto de salida ya existente.
        preset_sheet: Estilo de hoja preajustado.
        debug: Habilita el nivel de log DEBUG.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    validate_conflict_output_options(
        media_input_list=media_input_list,
        output=output,
        output_directory=output_directory,
    )
    for media_input in media_input_list:
        pipeline = SheetPipeline(debug=debug)
        pipeline.process_parameters(
            media_input=media_input,
            output=output,
            output_directory=output_directory,
            overwrite=overwrite,
            preset_sheet=preset_sheet,
        )
        if not pipeline.resolve_overwrite():
            continue
        pipeline.process_cmd()
