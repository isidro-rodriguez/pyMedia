"""Tipos y datos auxiliares compartidos por los modelos de pyMedia."""

from enum import Enum
from typing import NamedTuple

# =============================================================================
#  Enums
# =============================================================================


class OverwriteMode(Enum):
    """Resolución de conflicto si ya existe un fichero con el mismo nombre."""

    YES = "yes"
    NO = "no"
    ASK = "ask"


class OutputMediaType(Enum):
    """Tipos de ficheros multimedia de salida."""

    ANIMATED_IMAGE = "animated_image"
    AUDIO = "audio"
    GIF = "gif"
    IMAGE = "image"
    SUBTITLE = "subtitle"
    VIDEO = "video"


class PresetsSheetMode(Enum):
    """Presets de las hojas de concatenación de capturas."""

    FHD = "fhd"
    HD = "hd"
    WEB = "web"


class RotateMode(Enum):
    """Ángulos de giro disponibles."""

    D90 = 90
    D180 = 180
    D270 = 270


class ScaleMode(Enum):
    """Modo de redimensionado."""

    STRETCH = "stretch"  # Re-escala a la dimensión objetivo, modifica aspect ratio.
    FIT = "fit"  # Re-escala hasta encajar en la dimensión objetivo, no modifica AR.
    COVER = "cover"  # Re-escala hasta cubrir la dimensión objetivo, no modifica AR.


# =============================================================================
#  Tuples
# =============================================================================


class CropArea(NamedTuple):
    """Datos para el corte de imagen mediante crop."""

    width: int  # Ancho del vídeo resultante
    height: int  # Altura del vídeo resultante
    x: int  # Coordenada X del punto de corte
    y: int  # Coordenada Y del punto de corte


class Dimensions(NamedTuple):
    """Tipos de dimensiones."""

    width: int
    height: int


class ImageQuality(NamedTuple):
    """Parámetros para optimizar la calidad de la imagen de salida."""

    format: str
    compression: list[str]
