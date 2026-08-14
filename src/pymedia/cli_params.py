from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

from pymedia import locales

# -----------------------------------------------------------------------------
#  Enums de opciones
# -----------------------------------------------------------------------------


class GyrateMode(int, Enum):
    """Ángulos de giro disponibles"""

    d90 = 90
    d180 = 180
    d270 = 270


class OutputOnConflictMode(Enum):
    """Resolución de conflicto si ya existe un fichero con el mismo nombre"""

    FAIL = "fail"
    REPLACE = "replace"
    RENAME = "rename"
    SKIP = "skip"


class ScaleGifMode(int, Enum):
    """Alturas de fotograma disponibles"""

    P240 = 240
    P480 = 480
    P720 = 720


class ScaleVideoMode(int, Enum):
    """Alturas de fotograma disponibles"""

    P480 = 480
    P720 = 720
    P1080 = 1080
    P1440 = 1440
    P2160 = 2160


# -----------------------------------------------------------------------------
#  Auxiliar typer functions
# -----------------------------------------------------------------------------


def _show_help(ctx: typer.Context, value: bool) -> None:
    if value:
        typer.echo(ctx.get_help())
        raise typer.Exit()


def _validate_path(path: Path) -> Path | None:
    if not path.is_file():
        raise typer.BadParameter(locales.Cli["invalid_path"].format(path=path))
    return path


def _validate_path_list(path_list: list[Path]) -> list[Path] | None:
    for path in path_list:
        _validate_path(path)
    return path_list


# -----------------------------------------------------------------------------
#  Arguments
# -----------------------------------------------------------------------------


PathArgument = Annotated[
    Path,
    typer.Argument(help=locales.Cli["path_argument_help"], callback=_validate_path),
]

PathsArgument = Annotated[
    list[Path],
    typer.Argument(
        help=locales.Cli["paths_argument_help"], callback=_validate_path_list
    ),
]


# -----------------------------------------------------------------------------
#  Transcode options
# -----------------------------------------------------------------------------


CropOption = Annotated[
    str | None,
    typer.Option(
        "--crop",
        "-c",
        metavar="left,right,top,bottom",
        rich_help_panel="Encode options",
        help=locales.Cli["crop_help"],
    ),
]

DebugOption = Annotated[
    bool,
    typer.Option(
        "--debug",
        help=locales.Cli["debug_help"],
    ),
]

EndPointOption = Annotated[
    str | None,
    typer.Option(
        "--end-point",
        "-ep",
        metavar="hh:mm:ss",
        rich_help_panel="Encode options",
        help=locales.Cli["end_point_help"],
    ),
]

FpsOption = Annotated[
    int | None,
    typer.Option(
        "--fps",
        "-f",
        min=4,
        max=20,
        rich_help_panel="Encode options",
        help=locales.Cli["fps_help"],
    ),
]

GyrateOption = Annotated[
    GyrateMode | None,
    typer.Option(
        "--gyrate",
        "-g",
        rich_help_panel="Encode options",
        help=locales.Cli["gyrate_help"],
    ),
]

HelpOption = Annotated[
    bool,
    typer.Option(
        "--help",
        help=locales.Cli["show_help"],  # tu texto traducido
        callback=_show_help,
        is_eager=True,
        expose_value=False,
    ),
]

ScaleGifOption = Annotated[
    ScaleGifMode | None,
    typer.Option(
        "--scale",
        "-s",
        rich_help_panel="Encode options",
        help=locales.Cli["scale_gif_help"],
    ),
]

ScaleVideoOption = Annotated[
    ScaleVideoMode | None,
    typer.Option(
        "--scale",
        "-s",
        rich_help_panel="Encode options",
        help=locales.Cli["scale_video_help"],
    ),
]

StartPointOption = Annotated[
    str | None,
    typer.Option(
        "--start-point",
        "-sp",
        metavar="hh:mm:ss",
        rich_help_panel="Encode options",
        help=locales.Cli["start_point_help"],
    ),
]

RemuxOption = Annotated[
    bool,
    typer.Option(
        "--remux",
        "-r",
        rich_help_panel="Encode options",
        help=locales.Cli["remux_help"],
    ),
]

TrimPointsOption = Annotated[
    str,
    typer.Option(
        "--trim-points",
        "-t",
        metavar="00:10,00:20,00:30",
        rich_help_panel="Encode options",
        help=locales.Cli["trim_points_help"],
    ),
]


# -----------------------------------------------------------------------------
#  Output options
# -----------------------------------------------------------------------------


OutputOnConflictOption = Annotated[
    OutputOnConflictMode | None,
    typer.Option(
        "--on-conflict",
        "-oc",
        rich_help_panel="Output options",
        help=locales.Cli["output_on_conflict_help"],
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
