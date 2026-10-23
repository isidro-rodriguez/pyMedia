"""Comando ``play``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base.parameters import BaseParameters
from pymedia.errors import MissingParameterError
from pymedia.mixins.filters_mixin import FiltersMixin
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.playback_mixin import PlaybackMixin
from pymedia.mixins.timestamps_mixin import TimestampStartEndMixin
from pymedia.types import OverwriteMode, RotateMode, ScaleMode


@dataclass(kw_only=True)
class PlayParameters(
    BaseParameters,
    MediaInputMixin,
    TimestampStartEndMixin,
    PlaybackMixin,
    FiltersMixin,
):
    """Parámetros utilizados por el comando Play."""

    # La reproducción no escribe ficheros: no hay conflicto de sobrescritura.
    overwrite: OverwriteMode = OverwriteMode.NO

    @classmethod
    def load(
        cls,
        media_input: Path,
        timestamp_start: str | None = None,
        timestamp_end: str | None = None,
        audio_track: int | None = None,
        subtitles_track: int | None = None,
        subtitles_input: Path | None = None,
        no_subtitles: bool = False,
        mute: bool = False,
        volume: int | None = None,
        loop: bool = False,
        fullscreen: bool = False,
        crop: str | None = None,
        scale_to: str | None = None,
        scale_mode: ScaleMode = ScaleMode.FIT,
        scale_upscale: bool = False,
        rotate: RotateMode | None = None,
        hflip: bool = False,
        vflip: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            media_input: Ruta del fichero de vídeo a reproducir.
            timestamp_start: Marca de tiempo donde empieza la reproducción.
            timestamp_end: Marca de tiempo donde termina la reproducción.
            audio_track: Índice de la pista de audio a reproducir.
            subtitles_track: Índice de la pista de subtítulos a mostrar.
            subtitles_input: Fichero de subtítulos externo a dibujar.
            no_subtitles: Oculta los subtítulos del contenedor.
            mute: Reproduce sin audio.
            volume: Volumen inicial en porcentaje (0-100).
            loop: Repite la reproducción indefinidamente.
            fullscreen: Abre la ventana a pantalla completa.
            crop: Área y coordenada de la zona a preservar de la imagen.
            scale_to: Dimensión objetivo en píxeles.
            scale_mode: Política de escalado del vídeo o imagen.
            scale_upscale: Permite el incremento de dimensiones.
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
            hflip: Invierte la imagen horizontalmente.
            vflip: Invierte la imagen verticalmente.

        Returns:
            Parámetros procesados y validados para el comando play.

        Raises:
            MissingParameterError: Si el medio no se pudo obtener.
        """
        params = cls()

        params.create_media_input(media_input=media_input, logger=params.logger)
        if params.media is None:
            raise MissingParameterError(name="media")

        params.create_timestamp_start_end(
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )
        params.create_playback(
            logger=params.logger,
            audio_track=audio_track,
            subtitles_track=subtitles_track,
            subtitles_input=subtitles_input,
            no_subtitles=no_subtitles,
            mute=mute,
            volume=volume,
            loop=loop,
            fullscreen=fullscreen,
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
