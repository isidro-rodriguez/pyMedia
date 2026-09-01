from dataclasses import dataclass

from pymedia.data.types import RotateMode
from pymedia.errors import MissingParameterError


@dataclass(kw_only=True)
class RotateMixin:
    """Mixin para las rotar la imagen de un vídeo o captura.

    Attributes:
        rotate: Ángulo de rotación que se va a someter el vídeo.
    """

    rotate: RotateMode | None = None

    def create_rotate(self, rotate: RotateMode) -> None:
        """Crea el atributo rotate."""
        self.rotate = rotate

    def to_rotate_cmd(self) -> str:
        """Devuelve el filtro listo para consumo de ffmpeg."""
        if self.rotate is None:
            raise MissingParameterError(name="rotate")
        match self.rotate:
            case RotateMode.D90:
                return "transpose=1"
            case RotateMode.D180:
                return "transpose=1,transpose=1"
            case RotateMode.D270:
                return "transpose=2"
