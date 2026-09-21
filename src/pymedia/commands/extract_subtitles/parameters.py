"""Comando ``extract-subs``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import SubtitlesOutputMixin
from pymedia.mixins.streams_mixin import StreamsMixin
from pymedia.types import OverwriteMode, StreamsMode


@dataclass(kw_only=True)
class ExtractSubtitlesParameters(
    BaseParameters,
    MediaInputMixin,
    SubtitlesOutputMixin,
    StreamsMixin,
):
    """Parámetros utilizados por el comando ExtractSubtitles."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        subtitles_stream_tracks: str | None = None,
        subtitles_output: Path | None = None,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            subtitles_stream_tracks: Lista de índices de pistas en CSV; sin
                listado se extraen todas las pistas de subtítulos.
            subtitles_output: Ruta absoluta del fichero de subtítulos de salida.

        Returns:
            Parámetros procesados y validados para el comando extract-subs.

        Raises:
            InvalidContainerError: Si la extensión de salida no es un fichero
                de subtítulos soportado.
            InvalidRemuxError: Si el remux de una pista a la extensión de
                salida no es seguro.
            MissingParameterError: Si falta el medio, las pistas de subtítulos
                del medio o la salida procesada.
            MissingPropertyError: Si el medio no declara las pistas de
                subtítulos o el códec de alguna de ellas.
            UserError: Si el medio no tiene pistas de subtítulos, el formato
                del listado, algún índice o el nombre de salida no son válidos.
        """
        params = cls(overwrite=overwrite)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_streams(
            stream_tracks=subtitles_stream_tracks,
            streams_type=StreamsMode.SUBTITLES,
        )

        params.create_subtitles_output(
            extension=params.config.default_containers.subtitles,
            affix="_extracted_subs",
            output=subtitles_output,
        )

        return params
