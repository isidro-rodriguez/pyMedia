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


class ScaleMode(int, Enum):
    """Alturas de fotograma disponibles"""

    SD = 480
    HD = 720
    FHD = 1080
    QHD = 1440
    UHD = 2160


def _validate_path(path: Path) -> Path | None:
    if not path.is_file():
        raise typer.BadParameter(f"{path} no es un archivo")
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
    # TODO: validar formato, suma de px a recortar < resolución
    str | None,
    typer.Option(
        "--crop",
        "-c",
        metavar="IZQ,DER,ARRIBA,ABAJO",
        help="Recorta los pixeles indicados. [dim]Ej: -c 200,200,0,0[/dim]",
    ),
]

GyrateOption = Annotated[
    GyrateMode | None,
    typer.Option(
        "--gyrate",
        "-g",
        help="Gira el vídeo el ángulo indicado.\n[dim]Ej: -g 90[/dim]",
    ),
]

ScaleOption = Annotated[
    # TODO: ignorar, y notificar, si misma. Solicitar confirmación si redimensiona a mayor altura de pixeles. # noqa: E501
    ScaleMode | None,
    typer.Option(
        "--scale",
        "-s",
        help="Redimensiona proporcionalmente a la altura de indicada. [dim]Ej: -s 720[/dim]",  # noqa: E501
    ),
]

RemuxOption = Annotated[
    bool,
    typer.Option(
        "--remux", "-r", help="Recodifica con el perfil indicado en la configuración."
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
