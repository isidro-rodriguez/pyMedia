from enum import Enum
from pathlib import Path
from typing import Annotated

import typer

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


def _validate_path(path: Path) -> Path | None:
    if not path.is_file():
        raise typer.BadParameter(f"{path} is not a file.")
    return path


def _validate_path_list(path_list: list[Path]) -> list[Path] | None:
    for path in path_list:
        _validate_path(path)
    return path_list


# -----------------------------------------------------------------------------
#  Arguments
# -----------------------------------------------------------------------------


PathArgument = Annotated[
    Path, typer.Argument(help="Video to process.", callback=_validate_path)
]

PathsArgument = Annotated[
    list[Path],
    typer.Argument(help="Video list to process.", callback=_validate_path_list),
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
        help="Crops the specified number of pixels. [dim]E.g.: -c 200,200,0,0[/dim]",
    ),
]

DebugOption = Annotated[
    bool,
    typer.Option(
        "--debug",
        help="Log level DEBUG",
    ),
]

EndPointOption = Annotated[
    str | None,
    typer.Option(
        "--end-point",
        "-ep",
        metavar="hh:mm:ss",
        rich_help_panel="Encode options",
        help="Time point at which GIF generation ends. [dim]E.g.: -ep 1:20[/dim]",
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
        help="Frames per second of the animated GIF. [dim]E.g.: -f 12[/dim]",
    ),
]

GyrateOption = Annotated[
    GyrateMode | None,
    typer.Option(
        "--gyrate",
        "-g",
        rich_help_panel="Encode options",
        help="Rotate the media by the specified angle in degrees. [dim]E.g.: -g 90[/dim]",  # noqa: E501
    ),
]

ScaleGifOption = Annotated[
    ScaleGifMode | None,
    typer.Option(
        "--scale",
        "-s",
        rich_help_panel="Encode options",
        help="Resize the media proportionally to the specified height. [dim]E.g.: -s 240[/dim]",  # noqa: E501
    ),
]

ScaleVideoOption = Annotated[
    ScaleVideoMode | None,
    typer.Option(
        "--scale",
        "-s",
        rich_help_panel="Encode options",
        help="Resize the media proportionally to the specified height. [dim]E.g.: -s 240[/dim]",  # noqa: E501
    ),
]

StartPointOption = Annotated[
    str | None,
    typer.Option(
        "--start-point",
        "-sp",
        metavar="hh:mm:ss",
        rich_help_panel="Encode options",
        help="Time point at which GIF generation starts. [dim]E.g.: -sp 1:20[/dim]",  # noqa: E501
    ),
]

RemuxOption = Annotated[
    bool,
    typer.Option(
        "--remux",
        "-r",
        rich_help_panel="Encode options",
        help="Re-encodes using the profile specified in the configuration.",
    ),
]

TrimPointsOption = Annotated[
    str,
    typer.Option(
        "--trim-points",
        "-t",
        metavar="00:10,00:20,00:30",
        rich_help_panel="Encode options",
        help="Split points for the video. [dim]E.g.: -t 00:10,00:20,00:30[/dim]",
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
        help="Action to take if a file with the same name already exists. [dim]E.g.: -oc rename[/dim]",  # noqa: E501
    ),
]

OutputOption = Annotated[
    Path | None,
    typer.Option(
        "--output",
        "-o",
        rich_help_panel="Output options",
        help="Output file name. [dim]E.g.: -o cut.mp4[/dim]",
    ),
]
