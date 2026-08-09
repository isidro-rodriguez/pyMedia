# src/pymedia/cli_params.py
from enum import Enum
from pathlib import Path
from typing import Annotated

import typer


class GyrateMode(int, Enum):
    """Ángulos de giro disponibles"""

    d90 = 90
    d180 = 180
    d270 = 270


class ScaleGifMode(int, Enum):
    """Alturas de fotograma disponibles"""

    P240 = 240
    P480 = 480
    P720 = 720


class ScaleMode(int, Enum):
    """Alturas de fotograma disponibles"""

    P480 = 480
    P720 = 720
    P1080 = 1080
    P1440 = 1440
    P2160 = 2160


def _validate_path(path: Path) -> Path | None:
    if not path.is_file():
        raise typer.BadParameter(f"{path} no es un archivo.")
    return path


def _validate_path_list(path_list: list[Path]) -> list[Path] | None:
    for path in path_list:
        _validate_path(path)
    return path_list


PathArgument = Annotated[
    Path, typer.Argument(help="Vídeo a procesar.", callback=_validate_path)
]

PathsArgument = Annotated[
    list[Path],
    typer.Argument(help="Lista de vídeos a procesar.", callback=_validate_path_list),
]

CropOption = Annotated[
    str | None,
    typer.Option(
        "--crop",
        "-c",
        metavar="IZQ,DER,ARRIBA,ABAJO",
        help="Recorta los pixeles indicados. [dim]Ej: -c 200,200,0,0[/dim]",
    ),
]

EndPointOption = Annotated[
    str | None,
    typer.Option(
        "--end-point",
        "-ep",
        metavar="hh:mm:ss",
        help="Punto de tiempo en el que finaliza la generación del Gif. [dim]Ej: -ep 1:20[/dim]",  # noqa: E501
    ),
]

FpsOption = Annotated[
    int | None,
    typer.Option(
        "--fps",
        "-f",
        min=4,
        max=20,
        help="Imágenes por segundo del gif animado. [dim]Ej: -f 12[/dim]",
    ),
]

GyrateOption = Annotated[
    GyrateMode | None,
    typer.Option(
        "--gyrate",
        "-g",
        help="Gira el ángulo indicado.\n[dim]Ej: -g 90[/dim]",
    ),
]

ScaleGifOption = Annotated[
    ScaleGifMode | None,
    typer.Option(
        "--scale",
        "-s",
        help="Redimensiona proporcionalmente a la altura de indicada. [dim]Ej: -s 240[/dim]",  # noqa: E501
    ),
]

ScaleOption = Annotated[
    ScaleMode | None,
    typer.Option(
        "--scale",
        "-s",
        help="Redimensiona proporcionalmente a la altura de indicada. [dim]Ej: -s 720[/dim]",  # noqa: E501
    ),
]

StartPointOption = Annotated[
    str | None,
    typer.Option(
        "--start-point",
        "-sp",
        metavar="hh:mm:ss",
        help="Punto de tiempo en el que inicia la generación del Gif. [dim]Ej: -sp 1:20[/dim]",  # noqa: E501
    ),
]

RemuxOption = Annotated[
    bool,
    typer.Option(
        "--remux", "-r", help="Recodifica con el perfil indicado en la configuración."
    ),
]

OutputOption = Annotated[
    Path | None,
    typer.Option(
        "--output",
        "-o",
        help="Nombre del archivo de salida. [dim]Ej: -o corte.mp4[/dim]",
    ),
]

TrimPointsOption = Annotated[
    str,
    typer.Option(
        "--trim-points",
        "-t",
        metavar="00:10,00:20,00:30",
        help="Puntos de corte. [dim]Ej: -t 00:10,00:20,00:30[/dim]",
    ),
]
