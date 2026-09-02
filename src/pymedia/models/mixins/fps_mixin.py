"""Mixins de imágenes por segundo (GIF y extracción de capturas)."""

from dataclasses import dataclass
from fractions import Fraction

from pymedia.errors import MissingParameterError


@dataclass(kw_only=True)
class FpsGifMixin:
    """Mixin para las imágenes por segundo de un Gif.

    Attributes:
        fps: Imágenes por segundo del Gif.
    """

    fps: int | None = None

    def create_fps(self, fps: int) -> None:
        """Crea el atributo fps.

        Args:
            fps: Imágenes por segundo del Gif.
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
        fps: Frecuencia de imágenes por segundo a extraer
    """

    fps: Fraction | None = None

    def create_fps(self, every: int) -> None:
        """Crea el atributo fps, respecto a cada cuantos segundos se toma una imagen.

        Args:
            every: Cada cuantos segundos se extrae una imagen.
        """
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
