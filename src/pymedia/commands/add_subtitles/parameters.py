"""Comando ``add-subs``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.metadata_mixin import StripMetadataMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.mixins.subtitles_mixin import SubtitlesInputMixin
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class AddSubtitlesParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    SubtitlesInputMixin,
    StripMetadataMixin,
):
    """Parámetros utilizados por el comando AddSubtitles."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        subtitles_input: Path,
        language: str,
        title: str | None = None,
        media_output: Path | None = None,
        strip_metadata: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            subtitles_input: Ruta del fichero de subtítulos a insertar.
            language: Código ISO 639-2 del idioma de la pista.
            media_output: Ruta absoluta del fichero de salida procesado.
            title: Título descriptivo de la pista.
            strip_metadata: No copiar los metadatos del fichero de entrada.

        Returns:
            Parámetros procesados y validados para el comando add-subs.

        Raises:
            FfprobeError: Si ffprobe no puede leer el fichero de subtítulos.
            MissingArgumentError: Si no se recibió el argumento `language`.
            MissingParameterError: Si falta el medio o la salida procesada.
            UserError: Si el idioma no sigue el estándar ISO 639-2 o el
                contenedor de salida no soporta ningún códec de subtítulos.
        """
        params = cls(overwrite=overwrite, strip_metadata=strip_metadata)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_media_output(
            extension=media_input.suffix,
            affix="_added_subs",
            output=media_output,
        )

        params.create_add_subtitles(
            subtitles_input=subtitles_input.absolute(),
            language=language,
            title=title,
            logger=params.logger,
        )

        return params
