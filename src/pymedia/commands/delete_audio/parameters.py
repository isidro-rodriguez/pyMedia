"""Comando ``delete-audio``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.locales import _  # noqa
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.mixins.streams_mixin import StreamsMixin
from pymedia.types import OverwriteMode, StreamsMode


@dataclass(kw_only=True)
class DeleteAudioParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    StreamsMixin,
):
    """Parámetros utilizados por el comando DeleteAudio."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        audio_stream_tracks: str | None = None,
        media_output: Path | None = None,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            audio_stream_tracks: Lista de índices de pistas en CSV; sin
                listado se eliminan todas las pistas de audio.
            media_output: Ruta absoluta del fichero de salida procesado.

        Returns:
            Parámetros procesados y validados para el comando delete-audio.

        Raises:
            MissingParameterError: Si falta el medio, las pistas de audio del
                medio o la salida procesada.
            UserError: Si el formato del listado o algún índice no es válido.
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

        params.create_media_output(
            extension=media_input.suffix,
            affix="_deleted_audio",
            output=media_output,
        )

        return params
