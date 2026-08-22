from enum import Enum
from typing import NamedTuple


class CommandMode(Enum):
    """Nombres de los comandos disponibles en la CLI."""

    GIF = "gif"


class CropMargins(NamedTuple):
    """Datos para el corte de imagen mediante crop."""

    width: int  # Ancho del vídeo resultante
    height: int  # Altura del vídeo resultante
    x: int  # Coordenada X del punto de corte
    y: int  # Coordenada Y del punto de corte


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
