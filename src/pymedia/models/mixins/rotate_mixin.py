"""Mixin de rotación de la imagen (filtro transpose de ffmpeg)."""

from dataclasses import dataclass

from pymedia.errors import MissingParameterError
from pymedia.types import RotateMode


@dataclass(kw_only=True)
class RotateMixin:
    """Mixin para la rotación de la imagen de un vídeo o captura.

    Attributes:
        rotate: Ángulo ortogonal con el que se va a rotar la imagen.
    """

    rotate: RotateMode | None = None

    def create_rotate(self, rotate: RotateMode | None) -> None:
        """Crea el atributo rotate.

        Args:
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
        """
        if rotate is None:
            return
        self.rotate = rotate

    def to_rotate_cmd(self) -> str:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            El filtro `transpose` correspondiente al ángulo de rotación.

        Raises:
            MissingParameterError: Si no se ha definido el ángulo `rotate`.
        """
        if self.rotate is None:
            raise MissingParameterError(name="rotate")
        match self.rotate:
            case RotateMode.D90:
                return "transpose=1"
            case RotateMode.D180:
                return "transpose=1,transpose=1"
            case RotateMode.D270:
                return "transpose=2"
