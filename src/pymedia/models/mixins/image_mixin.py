"""Mixins de calidad de imagen de salida y detección de cambios de escena."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pymedia.errors import InvalidParameterError, MissingParameterError
from pymedia.locales import _  # noqa
from pymedia.types import ImageQuality


class _HasOutput(Protocol):
    image_output: Path


@dataclass(kw_only=True)
class ImageQualityMixin(_HasOutput):
    """Mixin para optimizar calidad y pixel_fmt dependiendo del formato de imagen."""

    def to_image_quality_cmd(self) -> ImageQuality:
        """Devuelve el filtro listo para consumo de ffmpeg."""
        match self.image_output.suffix:
            case ".jpg":
                return ImageQuality(
                    format="format=yuv420p",
                    compression=["-color_range", "2", "-q:v", "2"],
                )
            case ".png":
                return ImageQuality(
                    format="format=rgb24",
                    compression=["-compression_level", "6"],
                )
            case ".webp":
                return ImageQuality(
                    format="format=rgb24",
                    compression=["-lossless", "1"],
                )
            case _:
                raise InvalidParameterError(msg=_("Image container not supported."))


@dataclass(kw_only=True)
class SceneMixin:
    """Mixin indicar la obtención de imágenes por cambios de cámara en escena.

    Attributes:
        scene: Índice de sensibilidad de cambio de fotograma para obtener imagen.
    """

    scene: float | None = None

    def create_scene(self, scene: float | int | None) -> None:
        """Crea el parámetro scene.

        Args:
            scene: Índice de sensibilidad de cambio de escena.
        """
        if scene is None:
            return
        self.scene = scene

    def to_scene_cmd(self) -> str:
        """Devuelve el filtro listo para consumo de ffmpeg."""
        if self.scene is None:
            raise MissingParameterError(name="scene")
        return f"select='gt(scene,{self.scene})'"
