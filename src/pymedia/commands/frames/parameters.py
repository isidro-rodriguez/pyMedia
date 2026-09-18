"""Comando ``frames``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.filters_mixin import FiltersMixin
from pymedia.mixins.image_mixin import ImageQualityMixin
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import ImageOutputMixin
from pymedia.mixins.timestamps_mixin import TimestampAtMixin, TimestampStartEndMixin
from pymedia.types import OverwriteMode, RotateMode, ScaleMode


@dataclass(kw_only=True)
class FramesParameters(
    BaseParameters,
    MediaInputMixin,
    ImageOutputMixin,
    ImageQualityMixin,
    TimestampAtMixin,
    TimestampStartEndMixin,
    FiltersMixin,
):
    """Parámetros utilizados por el comando Frames.

    Incluye `TimestampStartEndMixin` aunque no exponga `--start`/`--end`: de él
    hereda `get_range_time()`, que resuelve el tramo a procesar de la barra de
    progreso.
    """

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        output: Path | None = None,
        timestamp_at: str | None = None,
        crop: str | None = None,
        rotate: RotateMode | None = None,
        scale_to: str | None = None,
        scale_mode: ScaleMode = ScaleMode.FIT,
        scale_upscale: bool = False,
        hflip: bool = False,
        vflip: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            output: Ruta absoluta del fichero de salida procesado.
            timestamp_at: Lista de marcas de tiempo a capturar.
            crop: Área y coordenada de la zona a preservar de la imagen.
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
            scale_to: Dimensión objetivo en píxeles.
            scale_mode: Política de escalado del vídeo o imagen.
            scale_upscale: Permite el incremento de dimensiones.
            hflip: Invierte la imagen horizontalmente.
            vflip: Invierte la imagen verticalmente.

        Returns:
            Parámetros procesados y validados para el comando frames.

        Raises:
            InvalidArgumentError: Si el formato del listado de marcas no es válido.
            InvalidContainerError: Si la extensión no es una imagen soportada.
            InvalidParameterError: Si el formato de imagen no está soportado.
            InvalidTimeFormatError: Si alguna marca no tiene un formato válido.
            MissingParameterError: Si falta el medio o la propiedad indicada.
            MissingPropertyError: Si el medio no declara alguna propiedad técnica.
            PermissionDeniedError: Si no se puede crear el directorio de salida.
            UserError: Si una marca supera la duración del vídeo o el nombre de
                salida contiene caracteres no permitidos.
        """
        params = cls(overwrite=overwrite)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_image_output(
            output=output,
            affix="_thumbnail",
            extension=params.config.default_containers.image,
        )

        params.create_timestamp_at(
            times_str=timestamp_at,
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

        return params
