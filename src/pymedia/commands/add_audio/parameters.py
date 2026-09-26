"""Comando ``add-audio``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.audio_mixin import AudioInputMixin
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.metadata_mixin import StripMetadataMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class AddAudioParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    AudioInputMixin,
    StripMetadataMixin,
):
    """Parámetros utilizados por el comando AddAudio."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        audio_input: Path,
        media_output: Path | None = None,
        strip_metadata: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            audio_input: Ruta del fichero de audio a insertar.
            media_output: Ruta absoluta del fichero de salida procesado.
            strip_metadata: No copiar los metadatos del fichero de entrada.

        Returns:
            Parámetros procesados y validados para el comando add-audio.

        Raises:
            FfprobeError: Si ffprobe no puede leer el fichero de audio externo.
            MissingParameterError: Si falta el medio o el fichero de audio.
            InvalidCodecContainerError: Si el códec del audio no es
                compatible con el contenedor de salida.
        """
        params = cls(overwrite=overwrite, strip_metadata=strip_metadata)

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
            logger=params.logger,
        )

        if params.media_output is not None:
            params.validate_audio_containers(params.media_output.suffix)

        return params
