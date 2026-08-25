from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from pymedia.errors import ConflictiveResizeParametersError, MissingMediaPropertyError
from pymedia.logger import Logger
from pymedia.models.media import Media


class _HasSingleMedia(Protocol):
    media: Media
    input_single: Path


class _Dimension(Enum):
    WIDTH = "width"
    HEIGHT = "height"


@dataclass(kw_only=True)
class ResizeMixin(_HasSingleMedia):
    """Mixin para los valores de redimensionado.

    Attributes:
        resize_width: Valor del ancho a redimensionar.
        resize_height: Valor de la altura a redimensionar.
        resize_upscale: Permite el incremento de dimensiones.
        resize_change_ratio: Permite el cambio de proporciones del vídeo.
    """

    resize_width: int | None = None
    resize_height: int | None = None
    resize_upscale: bool = False
    resize_change_ratio: bool = False

    def create_resize(
        self,
        logger: Logger,
        width: int | None = None,
        height: int | None = None,
        upscale: bool = False,
        change_ratio: bool = False,
    ) -> None:
        """Establece los parámetros de redimensionado.

        Args:
            upscale: Permite el incremento de dimensiones.
            change_ratio: Permite el cambio de proporciones.
            logger: Servicio de logueo.
            width: Ancho objetivo, en píxeles, o `None` si no se cambia.
            height: Altura objetivo, en píxeles, o `None` si no se cambia.

        Raises:
            InvalidResizeParametersError: Si se especifican tanto la altura como el
                ancho, pero sin permitir incremento de resolución o cambio de
                proporciones.
            MissingMediaPropertyError: Si los metadatos requeridos del vídeo no se
                pueden obtener.

        Warnings:
            resize_rejected_equal: Informa que no se escala si la altura elegida
                coincide con la altura del vídeo.
            upscale_rejected: Sin resize_upscale se informa que no se redimensiona si la
                altura elegida es mayor a la altura del vídeo.
        """

        if width is not None and height is not None and not change_ratio:
            raise ConflictiveResizeParametersError()

        self.resize_upscale = upscale
        self.resize_change_ratio = change_ratio
        self.resize_width = (
            _process_resize(
                resize=width,
                dimension=_Dimension.WIDTH,
                media=self.media,
                logger=logger,
            )
            if width is not None
            else None
        )
        self.resize_height = (
            _process_resize(
                resize=height,
                dimension=_Dimension.HEIGHT,
                media=self.media,
                logger=logger,
            )
            if height is not None
            else None
        )

    def to_resize_cmd(self) -> str | None:
        """Retorna el filtro de redimensionado listo para ffmpeg."""
        width, height = self.resize_width, self.resize_height
        if self.resize_change_ratio:
            if width is not None and height is not None:
                if self.resize_upscale:
                    return f"scale={width}:{height}"
                return f"scale='min({width},iw)':'min({height},ih)'"
            if width is not None:
                return f"scale={width}:ih"
            if height is not None:
                return f"scale=iw:{height}"
        if width is not None:
            if self.resize_upscale:
                return f"scale={width}:-2"
            return f"scale='min({width},iw)':-2"
        if height is not None:
            if self.resize_upscale:
                return f"scale=-2:{height}"
            return f"scale=-2:'min({height},ih)'"
        return None


def _process_resize(
    resize: int,
    dimension: _Dimension,
    media: Media,
    logger: Logger,
) -> int | None:
    """Valida y procesa la opción de redimensionado."""

    if dimension == _Dimension.WIDTH:
        if media.video is None or media.video.width is None:
            raise MissingMediaPropertyError(property_name="width")

        if resize == media.video.width:
            logger.warning(key="resize_rejected_equal", dimension="width")
            return None

        return resize

    if dimension == _Dimension.HEIGHT:
        if media.video is None or media.video.height is None:
            raise MissingMediaPropertyError(property_name="height")

        if resize == media.video.height:
            logger.warning(key="resize_rejected_equal", dimension="height")
            return None

        return resize

    return None
