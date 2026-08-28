from pathlib import Path
from typing import Annotated

import typer

from pymedia import locales
from pymedia.models.enums import (
    OverwriteMode,
    PresetsSheetMode,
)
from pymedia.services.typer_service import show_help, validate_path, validate_path_list

# -----------------------------------------------------------------------------
#  Argumentos
# -----------------------------------------------------------------------------


InputSingleArgument = Annotated[
    Path,
    typer.Argument(
        help=locales.Cli["path_argument_help"],
        callback=validate_path,
    ),
]

InputListArgument = Annotated[
    list[Path],
    typer.Argument(
        help=locales.Cli["path_list_argument_help"],
        callback=validate_path_list,
    ),
]


# -----------------------------------------------------------------------------
#  Opciones de aplicación
# -----------------------------------------------------------------------------


DebugOption = Annotated[
    bool,
    typer.Option(
        "--debug",
        help=locales.Cli["debug_help"],
    ),
]


HelpOption = Annotated[
    bool,
    typer.Option(
        "--help",
        help=locales.Cli["show_help"],  # tu texto traducido
        callback=show_help,
        is_eager=True,
        expose_value=False,
    ),
]


# -----------------------------------------------------------------------------
#  Opciones de salida
# -----------------------------------------------------------------------------

OutputDirectoryOption = Annotated[
    Path | None,
    typer.Option(
        "--directory",
        "-d",
        rich_help_panel="Output options",
        help=locales.Cli["output_directory_help"],
    ),
]

OutputOption = Annotated[
    Path | None,
    typer.Option(
        "--output",
        "-o",
        rich_help_panel="Output options",
        help=locales.Cli["output_help"],
    ),
]

OverwriteOption = Annotated[
    OverwriteMode,
    typer.Option(
        "--overwrite",
        "-ov",
        rich_help_panel="Output options",
        help=locales.Cli["overwrite_help"],
    ),
]


# -----------------------------------------------------------------------------
#  Opciones de comando
# -----------------------------------------------------------------------------


FpsGifOption = Annotated[
    int,
    typer.Option(
        "--fps",
        min=4,
        max=20,
        rich_help_panel="Command options",
        help=locales.Cli["fps_gif_help"],
    ),
]


PresetSheetOption = Annotated[
    PresetsSheetMode,
    typer.Option(
        "--preset",
        rich_help_panel="Command options",
        help=locales.Cli["preset_sheet_help"],
    ),
]


ResizeHeightOption = Annotated[
    int | None,
    typer.Option(
        "--height",
        rich_help_panel="Command options",
        help=locales.Cli["resize_height_help"],
    ),
]


ResizeWidthOption = Annotated[
    int | None,
    typer.Option(
        "--width",
        rich_help_panel="Command options",
        help=locales.Cli["resize_width_help"],
    ),
]


ResizeUpscaleOption = Annotated[
    bool,
    typer.Option(
        "--upscale",
        rich_help_panel="Command options",
        help=locales.Cli["resize_upscale_help"],
    ),
]


TimestampEndOption = Annotated[
    str | None,
    typer.Option(
        "--end",
        metavar="hh:mm:ss",
        rich_help_panel="Command options",
        help=locales.Cli["timestamp_end_help"],
    ),
]


TimestampStartOption = Annotated[
    str | None,
    typer.Option(
        "--start",
        metavar="hh:mm:ss",
        rich_help_panel="Command options",
        help=locales.Cli["timestamp_start_help"],
    ),
]
