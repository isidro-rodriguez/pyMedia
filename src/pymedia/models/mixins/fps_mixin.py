"""Mixins de la especificación de Friends per Second."""

from dataclasses import dataclass
from fractions import Fraction

from pymedia.errors import MissingParameterError


@dataclass(kw_only=True)
class FpsAnimatedMixin:
    """Mixin para los fps de imágenes animadas.

    Attributes:
        fps: Frames per second de la imagen animada.
    """

    fps: int | None = None

    def create_fps(self, fps: int) -> None:
        """Crea el atributo fps.

        Args:
            fps: Frames per second de la imagen animada.
        """
        self.fps = fps

    def to_fps_cmd(self) -> str:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            String con un filtro de ffmpeg.

        Raises:
            MissingParameterError: Si no se pudo obtener el parametro fps.
        """
        if self.fps is None:
            raise MissingParameterError(name="fps")
        return f"fps={self.fps}"


@dataclass(kw_only=True)
class FpsImageMixin:
    """Mixin para indicar las imágenes por segundo a extraer de un vídeo.

    Attributes:
        fps: Frecuencia de imágenes por segundo a extraer.
    """

    fps: Fraction | None = None

    def create_fps(self, every: int | None) -> None:
        """Crea el atributo fps, respecto a cada cuantos segundos se toma una imagen.

        Args:
            every: Cada cuantos segundos se extrae una imagen.
        """
        if every is None:
            return
        self.fps = Fraction(1, every)

    def to_fps_cmd(self) -> str:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            String con un filtro de ffmpeg.

        Raises:
            MissingParameterError: Si no se pudo obtener el parametro fps.
        """
        if self.fps is None:
            raise MissingParameterError(name="fps")
        return f"fps={self.fps}"
