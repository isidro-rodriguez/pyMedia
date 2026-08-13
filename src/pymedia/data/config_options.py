from enum import Enum

# -----------------------------------------------------------------------------
#  Enums de opciones de configuración
# -----------------------------------------------------------------------------


class AudioCodec(Enum):
    """Lista de códecs de audio disponibles en esta aplicación."""

    AAC = "aac"
    EAC3 = "eac3"
    OPUS = "opus"


class Channels(Enum):
    """Refiere al uso de canales de audio en uniones conflictivas."""

    MONO = "mono"
    STEREO = "stereo"
    SURROUND = "5.1"


class LoggerLevel(Enum):
    """Refiere a los niveles mínimos a los que va a loguear el servicio."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ResizeTo(Enum):
    """Refiere la altura en que se redimensionan los vídeos en uniones conflictivas."""

    MAX_HEIGHT = "max_height"
    MIN_HEIGHT = "min_height"


class TargetFPS(Enum):
    """
    Refiere al FPS en el que se transcodificarán los vídeos en uniones conflictivas.
    """

    MAX_FPS = "max_fps"
    MIN_FPS = "min_fps"


class VideoCodec(Enum):
    """Lista de códecs de vídeo disponibles en esta aplicación."""

    AV1 = "av1"
    H264 = "h264"
    H265 = "h265"
