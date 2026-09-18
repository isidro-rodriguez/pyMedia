"""Mixin que agrupa los filtros de imagen de ffmpeg para los comandos de vídeo."""

from dataclasses import dataclass

from pymedia.logger import Logger
from pymedia.mixins.crop_mixin import CropMixin
from pymedia.mixins.flip_mixin import FlipMixin
from pymedia.mixins.rotate_mixin import RotateMixin
from pymedia.mixins.scale_mixin import ScaleMixin
from pymedia.types import RotateMode, ScaleMode


@dataclass(kw_only=True)
class FiltersMixin(CropMixin, ScaleMixin, RotateMixin, FlipMixin):
    """Mixin que agrupa los filtros de imagen de ffmpeg.

    Hereda de `CropMixin`, `ScaleMixin`, `RotateMixin` y `FlipMixin` para
    crear y serializar todos los filtros de imagen en una única sentada.
    """

    def create_filters(
        self,
        logger: Logger,
        *,
        crop: str | None = None,
        rotate: RotateMode | None = None,
        scale_to: str | None = None,
        scale_upscale: bool = False,
        scale_mode: ScaleMode | None = None,
        hflip: bool = False,
        vflip: bool = False,
    ) -> None:
        """Crea los atributos de los filtros de imagen en una única llamada.

        Args:
            logger: Sistema de registro de mensajes.
            crop: String con el valor de crop indicado por el usuario.
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
            scale_to: Dimensión objetivo, en píxeles, o `None` si no se cambia.
            scale_upscale: Permite el incremento de dimensiones.
            scale_mode: Política de escalado; `None` conserva el valor actual.
            hflip: Invierte la imagen horizontalmente, intercambia izquierda y derecha.
            vflip: Invierte la imagen verticalmente, intercambiando arriba y abajo.
        """
        if scale_mode is not None:
            self.scale_mode = scale_mode
        self.create_crop(crop_str=crop)
        self.create_scale(
            logger=logger,
            scale_upscale=scale_upscale,
            scale_to=scale_to,
        )
        self.create_rotate(rotate=rotate)
        self.hflip = hflip
        self.vflip = vflip

    def to_filters_cmd(self) -> str:
        """Devuelve la cadena de filtros lista para el consumo de ffmpeg.

        Returns:
            Cadena con los filtros separados por coma, o una cadena vacía
            si no hay ningún filtro configurado.
        """
        filters: list[str] = []

        if self.crop_area is not None:
            filters.append(self.to_crop_cmd())

        if self.scale_to is not None:
            scale_filter = self.to_scale_cmd()
            if scale_filter is not None:
                filters.append(scale_filter)

        if self.hflip or self.vflip:
            filters.append(self.to_flip_cmd())

        if self.rotate is not None:
            filters.append(self.to_rotate_cmd())

        return ",".join(filters)
