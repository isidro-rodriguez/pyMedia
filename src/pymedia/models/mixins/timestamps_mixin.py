from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Protocol

from pymedia.errors import (
    InvalidTimeFormatError,
    MissingMediaPropertyError,
    MissingParameterError,
    TimeExceedsDurationError,
)
from pymedia.models.media import Media


class _HasSingleMedia(Protocol):
    media: Media
    input_single: Path


@dataclass(kw_only=True)
class TimestampStartMixin(_HasSingleMedia):
    """Mixin para las marcas de tiempo que indican el punto inicial a procesar.

    Attributes:
        timestamp_start: Marca de tiempo que indica el punto inicial.
    """

    timestamp_start: timedelta | None = None

    def create_timestamp_start(self, start: str | None) -> None:
        """Crea el atributo de marca de tiempo indicando el punto inicial.

        Args:
            start: String indicando punto inicial.

        Raises:
            InvalidTimeFormatError: Si el formato de la marca no es válido.
            MissingMediaPropertyError: Si no se pudo obtener la duración del vídeo.
            MissingParameterError: Si no se pudo obtener el parámetro.
            TimeExceedsDurationError: Si marca de tiempo superior a la duración.
        """
        self.timestamp_start = (
            _process_time(time_str=start, media=self.media)
            if start is not None
            else None
        )

    def to_timestamp_start_cmd(self) -> list[str]:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            Lista de strings lista para consumo de ffmpeg.
        """
        if self.timestamp_start is None:
            raise MissingParameterError(parameter="timestamp_start")
        return ["-ss", str(self.timestamp_start)]


@dataclass(kw_only=True)
class TimestampEndMixin(_HasSingleMedia):
    """Mixin para las marcas de tiempo que indican el punto final a procesar.

    Attributes:
        timestamp_end: Marca de tiempo que indica el punto final.
    """

    timestamp_end: timedelta | None = None

    def create_timestamp_end(self, end: str | None) -> None:
        """Crea el atributo de marca de tiempo indicando el punto final.

        Args:
            end: String indicando punto final.

        Raises:
            InvalidTimeFormatError: Si el formato de la marca no es válido.
            MissingMediaPropertyError: Si no se pudo obtener la duración del vídeo.
            MissingParameterError: Si no se pudo obtener el parámetro.
            TimeExceedsDurationError: Si marca de tiempo superior a la duración.
        """
        self.timestamp_end = (
            _process_time(time_str=end, media=self.media) if end is not None else None
        )

    def to_timestamp_end_cmd(self) -> list[str]:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            Lista de strings lista para consumo de ffmpeg.
        """
        if self.timestamp_end is None:
            raise MissingParameterError(parameter="timestamp_end")
        return ["-to", str(self.timestamp_end)]


def _process_time(
    time_str: str,
    media: Media,
) -> timedelta:
    """Valida y procesa la marca de tiempo."""

    def _parse_to_timedelta() -> timedelta:
        """Convierte str ('hh:mm:ss', 'mm:ss', 'ss') a timedelta."""
        parts = time_str.split(":")
        if not all(p.isdigit() for p in parts):
            raise InvalidTimeFormatError()
        match tuple(map(float, parts)):
            case (hours, minutes, seconds):
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)
            case (minutes, seconds):
                return timedelta(minutes=minutes, seconds=seconds)
            case (seconds,):
                return timedelta(seconds=seconds)
            case _:
                raise InvalidTimeFormatError()

    def _validate_time() -> None:
        """Valida que la marca de tiempo no supere la duración del vídeo."""
        if media.duration is None:
            raise MissingMediaPropertyError(property_name="video.duration")
        if time_delta > media.duration:
            raise TimeExceedsDurationError(
                time=str(time_delta), duration=str(media.duration)
            )

    time_delta = _parse_to_timedelta()
    _validate_time()

    return time_delta
