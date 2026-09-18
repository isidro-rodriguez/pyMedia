"""Tipos y datos auxiliares compartidos por los modelos de pyMedia."""

from enum import Enum
from typing import NamedTuple

# =============================================================================
#  Enums
# =============================================================================


class AudioCodecMode(Enum):
    """Lista de códecs de audio disponibles en esta aplicación."""

    AAC = "aac"
    EAC3 = "eac3"
    OPUS = "opus"


class AudioMode(Enum):
    """Modos de comandos de audio."""

    ADD = "add"
    DELETE = "delete"
    EDIT = "edit"
    EXTRACT = "extract"


class Channels(Enum):
    """Refiere al uso de canales de audio en uniones conflictivas."""

    MONO = "mono"
    STEREO = "stereo"
    SURROUND = "5.1"


class LanguageMode(Enum):
    """Locales disponibles en la aplicación, códigos ISO 639-2."""

    SYSTEM = "sys"
    ENGLISH = "eng"
    SPANISH = "spa"


class OverwriteMode(Enum):
    """Resolución de conflicto si ya existe un fichero con el mismo nombre."""

    YES = "yes"
    NO = "no"
    ASK = "ask"


class PresetsSheetMode(Enum):
    """Presets de las hojas de concatenación de capturas."""

    FHD = "fhd"
    HD = "hd"
    WEB = "web"


class PresetsTranscodeMode(Enum):
    """Presets de los perfiles de transcodificación presentes en config.toml."""

    FAST = "fast"
    EVEN = "even"
    SLOW = "slow"


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


class StreamsMode(Enum):
    """Tipos de streams presentes en un contenedor."""

    AUDIO = "audio"
    SUBTITLES = "subtitles"
    VIDEO = "video"


class SubtitlesMode(Enum):
    """Modelo de comando de subtítulos."""

    ADD = "add"
    DELETE = "delete"
    EDIT = "edit"
    EXTRACT = "extract"


class ThumbnailsMode(Enum):
    """Modos de comando de thumbnails."""

    FRAMES = "frames"
    INTERVAL = "interval"
    SCENE = "scene"


class VideoCodecMode(Enum):
    """Lista de códecs de vídeo modernos disponibles en esta aplicación."""

    AV1 = "av1"
    H264 = "h264"
    H265 = "h265"
    HEVC = "hevc"


# =============================================================================
#  Tuples
# =============================================================================


class CropArea(NamedTuple):
    """Datos para el corte de imagen mediante área."""

    width: int  # Ancho del vídeo resultante
    height: int  # Altura del vídeo resultante
    x: int  # Coordenada X del punto de corte
    y: int  # Coordenada Y del punto de corte


class CropBorders(NamedTuple):
    """Datos para el corte de imagen mediante bordes."""

    left: int
    right: int
    top: int
    bottom: int


class Dimensions(NamedTuple):
    """Tipos de dimensiones."""

    width: int
    height: int


class ImageQuality(NamedTuple):
    """Parámetros para optimizar la calidad de la imagen de salida."""

    format: str
    compression: list[str]
