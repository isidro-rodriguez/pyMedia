from enum import Enum
from typing import NamedTuple


class CropMargins(NamedTuple):
    """Datos para el corte de imagen mediante crop."""

    width: int  # Ancho del vídeo resultante
    height: int  # Altura del vídeo resultante
    x: int  # Coordenada X del punto de corte
    y: int  # Coordenada Y del punto de corte


class ContainerType(Enum):
    """Tipos de container."""

    ANIMATED = "animated"
    AUDIO = "audio"
    IMAGE = "image"
    VIDEO = "video"


class GyrateMode(int, Enum):
    """Ángulos de giro disponibles"""

    d90 = 90
    d180 = 180
    d270 = 270


class OverwriteMode(Enum):
    """Resolución de conflicto si ya existe un fichero con el mismo nombre"""

    YES = "yes"
    NO = "no"
    ASK = "ask"


class OutputMediaType(Enum):
    """Tipos de ficheros multimedia de salida."""

    ANIMATION = "animation"
    AUDIO = "audio"
    GIF = "gif"
    IMAGE = "image"
    SUBTITLE = "subtitle"
    VIDEO = "video"
