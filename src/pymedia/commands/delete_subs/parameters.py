"""Comando ``delete-subs``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.errors import MissingParameterError, UserError
from pymedia.locales import _  # noqa
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.mixins.streams_mixin import StreamsMixin
from pymedia.models.media import Media
from pymedia.types import OverwriteMode, StreamsMode


@dataclass(kw_only=True)
class DeleteSubtitlesParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    StreamsMixin,
):
    """Parámetros utilizados por el comando DeleteSubtitles."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        subtitles_stream_tracks: str | None = None,
        media_output: Path | None = None,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            subtitles_stream_tracks: Lista de índices de pistas en CSV; sin
                listado se eliminan todas las pistas de subtítulos.
            media_output: Ruta absoluta del fichero de salida procesado.

        Returns:
            Parámetros procesados y validados para el comando delete-subs.

        Raises:
            MissingParameterError: Si falta el medio, las pistas de subtítulos
                del medio o la salida procesada.
            UserError: Si el medio no tiene pistas de subtítulos, el formato
                del listado o algún índice no es válido.
        """
        params = cls(overwrite=overwrite)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_streams(
            stream_tracks=_resolve_tracks(
                media=params.media,
                stream_tracks=subtitles_stream_tracks,
            ),
            streams_type=StreamsMode.SUBTITLES,
        )

        params.create_media_output(
            extension=media_input.suffix,
            affix="_deleted_subs",
            output=media_output,
        )

        return params


def _resolve_tracks(media: Media | None, stream_tracks: str | None) -> str:
    """Resuelve el listado de pistas; sin listado, selecciona todas."""
    if stream_tracks is not None:
        return stream_tracks
    if media is None:
        raise MissingParameterError(name="media")
    if not media.subtitles:
        raise UserError(msg=_("The media file does not contain subtitles streams."))
    return ",".join(str(track.track_index) for track in media.subtitles)
