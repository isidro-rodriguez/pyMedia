"""Comando ``add-audio``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.audio_mixin import AudioInputMixin
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class AddAudioParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    AudioInputMixin,
):
    """Parámetros utilizados por el comando AddAudio."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        audio_input: Path,
        language: str | None,
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
            audio_input: Ruta del fichero de audio a insertar.
            language: Código ISO 639-2 del idioma de la pista.
            media_output: Ruta absoluta del fichero de salida procesado.
            title: Título descriptivo de la pista.
            forced: Fuerza al reproductor a usar la pista de audio.
            default: Se establece como la pista de audio por defecto del contenedor.
            hearing_impaired: Pista orientada a personas con problemas auditivos.
            commentary: Pista de comentarios de audio.

        Returns:
            Parámetros procesados y validados para el comando add-audio.

        Raises:
            FfprobeError: Si ffprobe no puede leer el fichero de audio externo.
            MissingArgumentError: Si no se recibió el argumento `language`.
            MissingParameterError: Si falta el medio o el fichero de audio.
            UserError: Si el idioma no sigue el estándar ISO 639-2.
        """
        params = cls(overwrite=overwrite)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_media_output(
            extension=media_input.suffix,
            affix="_added_audio",
            output=media_output,
        )

        params.create_add_audio(
            audio_input=audio_input.absolute(),
            language=language,
            logger=params.logger,
            title=title,
            forced=forced,
            default=default,
            hearing_impaired=hearing_impaired,
            commentary=commentary,
        )

        return params
