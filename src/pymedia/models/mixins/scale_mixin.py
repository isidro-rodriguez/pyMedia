"""Mixin de redimensionado (filtro scale de ffmpeg)."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from pymedia.data.types import Dimensions, ScaleMode
from pymedia.errors import (
    InvalidArgumentError,
    InvalidParameterError,
    MissingMediaPropertyError,
)
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.models.media import Media


class _HasSingleMedia(Protocol):
    media: Media
    input_single: Path


class _Dimension(Enum):
    WIDTH = "width"
    HEIGHT = "height"


@dataclass(kw_only=True)
class ScaleMixin(_HasSingleMedia):
    """Mixin para los valores de redimensionado.

    Attributes:
        scale_mode: Política de escalado del vídeo o imagen.
        scale_upscale: Permite el incremento de dimensiones.
        scale_to: Dimensión objetivo, en píxeles, o `None` si no se cambia.
    """

    scale_mode: ScaleMode
    scale_upscale: bool = False
    scale_to: Dimensions | None = None

    def create_scale(
        self,
        logger: Logger,
        scale_upscale: bool,
        scale_to: str,
    ) -> None:
        """Establece los parámetros de redimensionado.

        Args:
            logger: Sistema de registro de mensajes.
            scale_upscale: Permite el incremento de dimensiones.
            scale_to: Dimensión objetivo, en píxeles, o `None` si no se cambia.

        Raises:
            InvalidArgumentError: Si la dimensión objetivo no tiene un formato
                válido (se esperaba WIDTHxHEIGHT).
            InvalidParameterError: Si la dimensión objetivo no es par o el modo
                de escalado no tiene un valor válido.
            MissingMediaPropertyError: Si las dimensiones del vídeo no se
                pueden obtener.
        """
        self.scale_upscale = scale_upscale
        self.scale_to = self._process_scale(
            scale_str=scale_to, media=self.media, logger=logger
        )

    def to_scale_cmd(self) -> str | None:
        """Devuelve el valor de escala como filtro listo para el consumo de ffmpeg.

        Returns:
            String con el filtro listo para un comando ffmpeg. La dimensión no
            establecida en modos FIT/COVER se delega a ffmpeg (`-2`) para
            preservar la proporción original con precisión de subpíxel.
        """
        if self.scale_to is None:
            return None
        width = self.scale_to.width if self.scale_to.width != 0 else -2
        height = self.scale_to.height if self.scale_to.height != 0 else -2
        return f"scale={width}:{height}"

    def _process_scale(
        self, scale_str: str, media: Media, logger: Logger
    ) -> Dimensions | None:
        """Procesa el valor de escala validándolo según las opciones del usuario."""

        def _parse_dimensions(value: str) -> Dimensions:
            """Valida la entrada y la devuelve como un objeto de dimensiones."""
            try:
                width_str, height_str = value.split("x")
                width_int, height_int = int(width_str), int(height_str)
            except (ValueError, TypeError) as err:
                raise InvalidArgumentError(
                    msg=_("Invalid dimensions %(value)s. Expected: WIDTHxHEIGHT")
                    % {"value": value}
                ) from err
            return Dimensions(width_int, height_int)

        def _get_target_increment() -> tuple[float, _Dimension]:
            """Devuelve el incremento proporcional y la dimensión dominante."""
            if video is None or video.width is None or video.height is None:
                raise MissingMediaPropertyError(name=_("video dimensions"))
            width_proportion = target.width / video.width
            height_proportion = target.height / video.height
            if self.scale_mode == ScaleMode.FIT:
                if width_proportion <= height_proportion:
                    return width_proportion, _Dimension.WIDTH
                return height_proportion, _Dimension.HEIGHT
            elif self.scale_mode == ScaleMode.COVER:
                if width_proportion >= height_proportion:
                    return width_proportion, _Dimension.WIDTH
                return height_proportion, _Dimension.HEIGHT
            else:
                raise InvalidParameterError(msg=_("Scale mode not supported."))

        video = media.video
        if video is None or video.width is None or video.height is None:
            raise MissingMediaPropertyError(name=_("video dimensions"))

        target = _parse_dimensions(scale_str)

        if target.width % 2 != 0 or target.height % 2 != 0:
            raise InvalidParameterError(msg=_("Target dimensions must be even."))

        if video.width == target.width and video.height == target.height:
            return None

        msg = _("Ignored scale. Target scale > video resolution, it requires upscale.")
        match self.scale_mode:
            case ScaleMode.STRETCH:
                if self.scale_upscale:
                    return target
                if video.width < target.width or video.height < target.height:
                    logger.warning(msg=msg)
                    return None
                return target
            case ScaleMode.FIT | ScaleMode.COVER:
                target_increment, dominant_dimension = _get_target_increment()
                if not self.scale_upscale and target_increment >= 1:
                    logger.warning(msg=msg)
                    return None
                if dominant_dimension == _Dimension.WIDTH:
                    target = target._replace(height=0)
                else:
                    target = target._replace(width=0)
                return target
