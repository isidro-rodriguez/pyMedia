"""Comando ``animated``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.filters_mixin import FiltersMixin
from pymedia.mixins.fps_mixin import FpsAnimatedMixin
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import AnimatedOutputMixin
from pymedia.mixins.timestamps_mixin import TimestampStartEndMixin
from pymedia.types import OverwriteMode, RotateMode, ScaleMode


@dataclass(kw_only=True)
class AnimatedParameters(
    BaseParameters,
    MediaInputMixin,
    AnimatedOutputMixin,
    FpsAnimatedMixin,
    FiltersMixin,
    TimestampStartEndMixin,
):
    """Parámetros utilizados por el comando Animated."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        show_cmd: bool,
        media_input: Path,
        fps: int,
        scale_mode: ScaleMode,
        output: Path | None = None,
        timestamp_start: str | None = None,
        timestamp_end: str | None = None,
        crop: str | None = None,
        scale_to: str | None = None,
        scale_upscale: bool = False,
        rotate: RotateMode | None = None,
        hflip: bool = False,
        vflip: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            show_cmd: Muestra al usuario el comando ffmpeg compuesto pero no lo ejecuta.
            media_input: Ruta del fichero de vídeo a procesar.
            fps: Fotogramas por segundo de la imagen animada generado.
            scale_mode: Política de escalado del vídeo o imagen.
            output: Ruta absoluta del fichero de salida procesado.
            timestamp_start: Marca de tiempo que indica el punto inicial.
            timestamp_end: Marca de tiempo que indica el punto final.
            crop: Área y coordenada de la zona a preservar de la imagen.
            scale_to: Dimensión objetivo en píxeles.
            scale_upscale: Permite el incremento de dimensiones.
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
            hflip: Invierte la imagen horizontalmente.
            vflip: Invierte la imagen verticalmente.

        Returns:
            Parámetros procesados y validados para el comando animated.
        """
        params = cls(overwrite=overwrite, fps=fps)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_animated_output(
            output=output,
            extension=params.config.default_containers.animated_image,
        )

        params.create_filters(
            logger=params.logger,
            crop=crop,
            scale_to=scale_to,
            scale_upscale=scale_upscale,
            scale_mode=scale_mode,
            rotate=rotate,
            hflip=hflip,
            vflip=vflip,
        )

        params.create_timestamp_start_end(
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )

        return params
