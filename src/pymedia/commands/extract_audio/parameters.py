"""Comando ``extract-audio``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import AudioOutputMixin
from pymedia.mixins.streams_mixin import StreamsMixin
from pymedia.types import OverwriteMode, StreamsMode


@dataclass(kw_only=True)
class ExtractAudioParameters(
    BaseParameters,
    MediaInputMixin,
    AudioOutputMixin,
    StreamsMixin,
):
    """Parámetros utilizados por el comando ExtractAudio."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        audio_stream_tracks: str | None = None,
        audio_output: Path | None = None,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            audio_stream_tracks: Lista de índices de pistas en CSV; sin
                listado se extraen todas las pistas de audio.
            audio_output: Ruta absoluta del fichero de audio de salida.

        Returns:
            Parámetros procesados y validados para el comando extract-audio.

        Raises:
            InvalidContainerError: Si la extensión de salida no es una pista
                de audio soportada.
            InvalidRemuxError: Si el remux de una pista a la extensión de
                salida no es seguro.
            MissingParameterError: Si falta el medio, las pistas de audio del
                medio o la salida procesada.
            MissingPropertyError: Si el medio no declara las pistas de audio o
                el códec de alguna de ellas.
            UserError: Si el formato del listado, algún índice o el nombre de
                salida no son válidos.
        """
        params = cls(overwrite=overwrite)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_streams(
            stream_tracks=audio_stream_tracks,
            streams_type=StreamsMode.AUDIO,
        )

        params.create_audio_output(
            extension=params.config.default_containers.audio_track,
            affix="_extracted_audio",
            output=audio_output,
        )

        return params
