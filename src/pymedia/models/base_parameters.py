from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import NamedTuple, TypeVar


class CommandMode(Enum):
    """Nombres de los comandos disponibles en la CLI."""

    CONCAT = "concat"
    ENCODE = "encode"
    SPLIT = "split"
    GIF = "gif"


class CropMargins(NamedTuple):
    """Datos para el corte de imagen mediante crop."""

    width: int  # Ancho del vídeo resultante
    height: int  # Altura del vídeo resultante
    x: int  # Coordenada X del punto de corte
    y: int  # Coordenada Y del punto de corte

    def to_cmd(self) -> str:
        """Retorna el string para el filtro de crop."""
        return f"crop={self.width}:{self.height}:{self.x}:{self.y}"


class GyrateMode(int, Enum):
    """Ángulos de giro disponibles"""

    d90 = 90
    d180 = 180
    d270 = 270

    def to_cmd(self) -> str:
        """Retorna el string para el filtro de giro."""
        return {
            GyrateMode.d90: "transpose=1",
            GyrateMode.d180: "vflip,hflip",
            GyrateMode.d270: "transpose=2",
        }[self]


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

    def to_cmd(self, reject_increase: bool = False) -> str:
        """Retorna el string para el filtro de giro."""
        return (
            f"scale=-2:min({self.value}\\,ih)"
            if reject_increase
            else f"scale=-2:{self.value}"
        )


class ScaleVideoMode(int, Enum):
    """Alturas de fotograma disponibles"""

    P480 = 480
    P720 = 720
    P1080 = 1080
    P1440 = 1440
    P2160 = 2160

    def to_cmd(self, reject_increase: bool = False) -> str:
        """Retorna el string para el filtro de giro."""
        return (
            f"scale=-2:min({self.value}\\,ih)"
            if reject_increase
            else f"scale=-2:{self.value}"
        )


ScaleModeT = TypeVar("ScaleModeT", ScaleVideoMode, ScaleGifMode)


@dataclass(slots=True, kw_only=True)
class BaseParameters:
    """
    Parámetros comunes para todos los comandos.

    Attributes:
        debug: Si se activa el modo Debug para más información.
        output: Ruta del fichero de salida.
        output_on_conflict: Actuación en caso de fichero de salida ya existente.
    """

    debug: bool = False
    output: Path
    output_on_conflict: OutputOnConflictMode = OutputOnConflictMode.FAIL
