from pathlib import Path
from typing import Annotated

import typer

from pymedia import locales
from pymedia.models.enums import (
    OverwriteMode,
)
from pymedia.services.typer_service import show_help, validate_path

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


EndOption = Annotated[
    str | None,
    typer.Option(
        "--end",
        metavar="hh:mm:ss",
        rich_help_panel="Command options",
        help=locales.Cli["end_point_help"],
    ),
]


FpsOption = Annotated[
    int,
    typer.Option(
        "--fps",
        min=4,
        max=20,
        rich_help_panel="Command options",
        help=locales.Cli["fps_help"],
    ),
]


ScaleGifOption = Annotated[
    int,
    typer.Option(
        "--scale",
        min=240,
        max=720,
        rich_help_panel="Command options",
        help=locales.Cli["scale_help"],
    ),
]


StartOption = Annotated[
    str | None,
    typer.Option(
        "--start",
        metavar="hh:mm:ss",
        rich_help_panel="Command options",
        help=locales.Cli["start_point_help"],
    ),
]
