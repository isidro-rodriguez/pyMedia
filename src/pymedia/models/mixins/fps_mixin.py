from dataclasses import dataclass

from pymedia.errors import MissingParameterError


@dataclass(kw_only=True)
class FpsGifMixin:
    """Mixin para las imágenes por segundo de un Gif.

    Attributes:
        fps: Imágenes por segundo del Gif.
    """

    fps: int | None = None

    def create_fps(self, fps: int) -> None:
        """Crea el atributo fps."""
        self.fps = fps

    def to_fps_cmd(self) -> str:
        """Devuelve el filtro listo para consumo de ffmpeg."""
        if self.fps is None:
            raise MissingParameterError(name="fps")
        return f"fps={self.fps}"
