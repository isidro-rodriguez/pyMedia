"""Mixin para listados de streams proporcionados por el usuario."""

from dataclasses import dataclass
from typing import Protocol

from pymedia.errors import (
    AudioError,
    InvalidArgumentError,
    InvalidParameterError,
    MissingArgumentError,
    MissingParameterError,
    SubtitlesError,
)
from pymedia.locales import _  # noqa
from pymedia.models.media import Media
from pymedia.types import StreamsMode


class _HasMedia(Protocol):
    """Objeto que expone la ruta y los metadatos del fichero de entrada."""

    media: Media


@dataclass(kw_only=True)
class StreamsMixin(_HasMedia):
    """Mixin para listados de streams proporcionados por el usuario.

    Los índices de pistas de streams se validan que presentan enumeración correcta y
    presente dentro de la lista de streams del tipo indicado.

    Attributes:
         stream_tracks: Lista de pistas de emisiones.
    """

    stream_tracks: list[int] | None = None

    def create_streams(
        self, stream_tracks: str | None, streams_type: StreamsMode
    ) -> None:
        """Añade la lista de streams como parámetro validado."""
        if stream_tracks is None:
            raise MissingArgumentError(name="stream_tracks")

        track_list: list[int] = self._parse_stream_list(stream_tracks_str=stream_tracks)

        for track in track_list:
            self._validate_stream(track=track, streams_type=streams_type)

        self.stream_tracks = track_list

    @staticmethod
    def _parse_stream_list(stream_tracks_str: str) -> list[int]:
        """Parsea el string a lista de enteros."""
        try:
            stream_tracks: list[int] = [int(x) for x in stream_tracks_str.split(",")]
        except ValueError as err:
            raise InvalidArgumentError(
                msg=_(
                    "Incorrect stream tracks format. Expected comma separated integers."
                )
            ) from err
        return stream_tracks

    def _validate_stream(self, track: int, streams_type: StreamsMode) -> None:
        """Valida que el índice de stream, del tipo buscado, está presente."""
        if self.media is None:
            raise MissingParameterError(name="media")
        if track < 0:
            raise InvalidArgumentError(msg=_("Stream index must be greater than 0."))

        match streams_type:
            case StreamsMode.AUDIO:
                if self.media.audio is None:
                    raise MissingParameterError(name="media.audio")

                for audio in self.media.audio:
                    if track == audio.track_index:
                        return
                raise AudioError(msg=_("Audio index not included."))
            case StreamsMode.SUBTITLES:
                if self.media.subtitles is None:
                    raise MissingParameterError(name="media.subtitles")

                for subtitles in self.media.subtitles:
                    if track == subtitles.track_index:
                        return
                raise SubtitlesError(msg=_("Subtitles index not included."))
            case StreamsMode.VIDEO:
                # Manipulación de streams de vídeo todavía no soportadas.
                pass

        raise InvalidParameterError(msg=_("Incorrect stream type."))
