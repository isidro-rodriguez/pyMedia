"""Comando ``transcode``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.errors import MissingParameterError
from pymedia.ffprobe import validate_subtitles_file_codec
from pymedia.mixins.filters_mixin import FiltersMixin
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.mixins.streams_mixin import StreamsMixin
from pymedia.mixins.transcode_mixin import TranscodeMixin
from pymedia.models.config import Config
from pymedia.types import (
    OverwriteMode,
    PresetsTranscodeMode,
    RotateMode,
    ScaleMode,
    StreamsMode,
)


@dataclass(kw_only=True)
class TranscodeParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    StreamsMixin,
    TranscodeMixin,
    FiltersMixin,
):
    """Parámetros utilizados por el comando Transcode."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        preset_transcode: PresetsTranscodeMode,
        output: Path | None = None,
        output_directory: Path | None = None,
        transcode_audio: str | None = None,
        transcode_video: bool = False,
        subtitles_input: Path | None = None,
        crop: str | None = None,
        scale_to: str | None = None,
        scale_mode: ScaleMode = ScaleMode.FIT,
        scale_upscale: bool = False,
        rotate: RotateMode | None = None,
        hflip: bool = False,
        vflip: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados para un vídeo.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            preset_transcode: Perfil de transcodificación de config.toml.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de ficheros.
            transcode_audio: Lista de pistas de audio a transcodificar.
            transcode_video: Transcodifica la pista de vídeo.
            subtitles_input: Subtítulos a quemar en la pista de vídeo.
            crop: Área y coordenada de la zona a preservar de la imagen.
            scale_to: Dimensión objetivo en píxeles.
            scale_mode: Política de escalado del vídeo o imagen.
            scale_upscale: Permite el incremento de dimensiones.
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
            hflip: Invierte la imagen horizontalmente.
            vflip: Invierte la imagen verticalmente.

        Returns:
            Parámetros procesados y validados para el comando transcode.

        Raises:
            FfprobeError: Si ffprobe no puede leer el fichero de subtítulos
                externo o no detecta un formato compatible.
            MissingParameterError: Si el medio no se pudo obtener.
        """
        # Filtros de imagen y quemado de subtítulos obligan a transcodificar el vídeo.
        if not all(
            [
                subtitles_input is None,
                crop is None,
                scale_to is None,
                rotate is None,
                hflip is False,
                vflip is False,
            ]
        ):
            transcode_video = True

        params = cls(
            overwrite=overwrite,
            transcode=getattr(Config.load().transcode, preset_transcode.value),
            transcode_video=transcode_video,
            subtitles_input=subtitles_input,
        )

        params.create_media_input(media_input=media_input, logger=params.logger)
        if params.media is None:
            raise MissingParameterError(name="media")

        if subtitles_input is not None:
            validate_subtitles_file_codec(
                subtitles_input=subtitles_input,
                logger=params.logger,
            )

        params.create_media_output(
            extension=params.config.default_containers.media,
            affix="_transcoded",
            output=output,
            output_directory=output_directory,
        )
        params.create_streams(
            stream_tracks=transcode_audio,
            streams_type=StreamsMode.AUDIO,
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
