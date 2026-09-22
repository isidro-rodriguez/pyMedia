"""Comando ``sheet``: cli."""

import typer

from pymedia.commands.base_cli import validate_conflict_output_options
from pymedia.commands.base_cli_options import (
    DebugOption,
    HelpOption,
    MediaInputListArgument,
    OutputDirectoryOption,
    OutputOption,
    OverwriteOption,
    PresetSheetOption,
    ShowCmdOption,
)
from pymedia.commands.sheet.parameters import SheetParameters
from pymedia.commands.sheet.service import SheetService
from pymedia.locales import _
from pymedia.logger import Logger
from pymedia.types import OverwriteMode, PresetsSheetMode

sheet_cli = typer.Typer()


SHEET_HELP = _(
    """\
Generates a thumbnail grid sheet with metadata information.

[bold]Examples[/bold]:
  Generate a vcs with default HD preset:
    > pymedia sheet input.mp4
  Generates a vcs with different preset and specified output:
    > pymedia sheet input.mp4 --preset fhd -o vcs.webp
"""
)


@sheet_cli.command(
    name="sheet",
    help=SHEET_HELP,
    rich_help_panel=_("Analysis commands"),
    no_args_is_help=True,
)
def sheet(
    media_input_list: MediaInputListArgument,
    output: OutputOption = None,
    output_directory: OutputDirectoryOption = None,
    overwrite: OverwriteOption = OverwriteMode.ASK,
    preset_sheet: PresetSheetOption = PresetsSheetMode.HD,
    debug: DebugOption = False,
    show_cmd: ShowCmdOption = False,
    help_: HelpOption = False,
) -> None:
    """Punto de entrada del comando ``sheet``.

    Args:
        media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
        output: Ruta absoluta del fichero de salida procesado.
        output_directory: Directorio de salida para lotes de ficheros.
        overwrite: Política ante conflicto de salida ya existente.
        preset_sheet: Estilo de hoja preajustado.
        debug: Habilita el nivel de log DEBUG.
        show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
        help_: Helper para mostrar esta línea en distintos idiomas.
    """
    validate_conflict_output_options(
        media_input_list=media_input_list,
        output=output,
        output_directory=output_directory,
    )

    Logger.create(debug=debug)
    for media_input in media_input_list:
        params = SheetParameters.load(
            overwrite=overwrite,
            media_input=media_input,
            output=output,
            output_directory=output_directory,
            preset_sheet=preset_sheet,
        )
        SheetService(debug=debug, show_cmd=show_cmd, params=params).start()
