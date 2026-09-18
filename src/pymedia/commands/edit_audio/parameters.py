"""Comando ``edit-audio``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.errors import MissingParameterError
from pymedia.mixins.audio_mixin import AudioInputMixin
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.mixins.streams_mixin import StreamsMixin
from pymedia.types import OverwriteMode, StreamsMode


@dataclass(kw_only=True)
class EditAudioParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    StreamsMixin,
    AudioInputMixin,
):
    """Parámetros utilizados por el comando EditAudio."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        audio_stream_tracks: str | None = None,
        language: str | None = None,
        media_output: Path | None = None,
        title: str | None = None,
        forced: bool = False,
        default: bool = False,
        hearing_impaired: bool = False,
        commentary: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            audio_stream_tracks: Índice de la pista de audio a editar.
            language: Código ISO 639-2 del idioma de la pista.
            media_output: Ruta absoluta del fichero de salida procesado.
            title: Título descriptivo de la pista.
            forced: Fuerza al reproductor a usar la pista de audio.
            default: Se establece como la pista de audio por defecto del contenedor.
            hearing_impaired: Pista orientada a personas con problemas auditivos.
            commentary: Pista de comentarios de audio.

        Returns:
            Parámetros procesados y validados para el comando edit-audio.

        Raises:
            MissingParameterError: Si falta la pista a editar, el medio, las
                pistas de audio del medio o la salida procesada.
            UserError: Si el idioma no sigue el estándar ISO 639-2 o la pista
                indicada no existe en el contenedor.
        """
        if audio_stream_tracks is None:
            raise MissingParameterError(name="audio_stream_tracks")

        params = cls(overwrite=overwrite)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_media_output(
            extension=media_input.suffix,
            affix="_edited_audio",
            output=media_output,
        )

        params.create_streams(
            stream_tracks=audio_stream_tracks,
            streams_type=StreamsMode.AUDIO,
        )

        params.create_edit_audio(
            language=language,
            title=title,
            forced=forced,
            default=default,
            hearing_impaired=hearing_impaired,
            commentary=commentary,
        )

        return params
