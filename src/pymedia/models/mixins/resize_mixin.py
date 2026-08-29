from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol

from pymedia.errors import (
    ConflictiveResizeDimensionsParametersError,
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
class ResizeMixin(_HasSingleMedia):
    """Mixin para los valores de redimensionado.

    Attributes:
        resize_width: Valor del ancho a redimensionar.
        resize_height: Valor de la altura a redimensionar.
        resize_upscale: Permite el incremento de dimensiones.
    """

    resize_width: int | None = None
    resize_height: int | None = None
    resize_upscale: bool = False

    def create_resize(
        self,
        logger: Logger,
        width: int | None = None,
        height: int | None = None,
        upscale: bool = False,
    ) -> None:
        """Establece los parámetros de redimensionado.

        Args:
            upscale: Permite el incremento de dimensiones.
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

        if width is not None and height is not None:
            raise ConflictiveResizeDimensionsParametersError()

        self.resize_upscale = upscale
        self.resize_width = (
            self._process_resize(
                resize=width,
                dimension=_Dimension.WIDTH,
                upscale=self.resize_upscale,
                media=self.media,
                logger=logger,
            )
            if width is not None
            else None
        )
        self.resize_height = (
            self._process_resize(
                resize=height,
                dimension=_Dimension.HEIGHT,
                upscale=self.resize_upscale,
                media=self.media,
                logger=logger,
            )
            if height is not None
            else None
        )

    def to_resize_cmd(self) -> str | None:
        """Retorna el filtro de redimensionado listo para ffmpeg."""
        width, height = self.resize_width, self.resize_height
        if width is not None:
            if self.resize_upscale:
                return f"scale={width}:-2"
            return f"scale='min({width},iw)':-2"
        if height is not None:
            if self.resize_upscale:
                return f"scale=-2:{height}"
            return f"scale=-2:'min({height},ih)'"
        return None

    @staticmethod
    def _process_resize(
        resize: int,
        dimension: _Dimension,
        upscale: bool,
        media: Media,
        logger: Logger,
    ) -> int | None:
        """Valida y procesa la opción de redimensionado."""

        if dimension == _Dimension.WIDTH:
            if media.video is None or media.video.width is None:
                raise MissingMediaPropertyError(name="width")

            if resize == media.video.width:
                logger.warning(
                    _("Resize rejected cause %(dimension)s is equal."),
                    dimension="width",
                )
                return None

            if resize > media.video.width and upscale is False:
                logger.warning(
                    _(
                        "Resize rejected cause no_upscale is True and target "
                        "%(target)s is greater than source %(source)s."
                    ),
                    target=resize,
                    source=media.video.width,
                )
                return None

            return resize

        if dimension == _Dimension.HEIGHT:
            if media.video is None or media.video.height is None:
                raise MissingMediaPropertyError(name="height")

            if resize == media.video.height:
                logger.warning(
                    _("Resize rejected cause %(dimension)s is equal."),
                    dimension="height",
                )
                return None

            if resize > media.video.height and upscale is False:
                logger.warning(
                    _(
                        "Resize rejected cause no_upscale is True and target "
                        "%(target)s is greater than source %(source)s."
                    ),
                    target=resize,
                    source=media.video.height,
                )
                return None

            return resize

        return None
