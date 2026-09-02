"""Mixins de marcas de tiempo de inicio, fin y listas de marcas."""

import re
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Protocol

from pymedia.errors import (
    InvalidArgumentError,
    InvalidParameterError,
    InvalidTimeFormatError,
    MissingMediaPropertyError,
    MissingParameterError,
)
from pymedia.locales import _  # noqa
from pymedia.models.media import Media


class _HasSingleMedia(Protocol):
    media: Media
    input_single: Path


@dataclass(kw_only=True)
class TimestampStartEndMixin(_HasSingleMedia):
    """Mixin para las marcas de tiempo que indican el punto inicial a procesar.

    Attributes:
        timestamp_start: Marca de tiempo que indica el punto inicial.
    """

    timestamp_start: timedelta | None = None
    timestamp_end: timedelta | None = None

    def create_timestamp_start_end(
        self, timestamp_start: str | None, timestamp_end: str | None
    ) -> None:
        """Crea el atributo de marca de tiempo indicando el punto inicial.

        Args:
            timestamp_start: Marca de tiempo que indica el punto inicial.
            timestamp_end: Marca de tiempo que indica el punto final.

        Raises:
            InvalidTimeFormatError: Si el formato de la marca no es válido.
            MissingMediaPropertyError: Si no se pudo obtener la duración del vídeo.
            MissingParameterError: Si no se pudo obtener el parámetro.
            TimeExceedsDurationError: Si marca de tiempo superior a la duración.
        """
        if timestamp_start is not None:
            self.timestamp_start = _process_time(
                time_str=timestamp_start,
                media=self.media,
            )

        if timestamp_end is not None:
            self.timestamp_end = _process_time(
                time_str=timestamp_end,
                media=self.media,
            )

        if self.timestamp_start is not None and self.timestamp_end is not None:
            if self.timestamp_start > self.timestamp_end:
                raise InvalidParameterError(
                    msg=_("Invalid timestamps. Start (%(start)s) => End (%(end)s.)")
                    % {"start": timestamp_start, "end": timestamp_end}
                )

    def to_timestamp_start_cmd(self) -> list[str]:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            Lista de strings lista para consumo de ffmpeg.
        """
        if self.timestamp_start is None:
            raise MissingParameterError(name="timestamp_start")
        return ["-ss", str(self.timestamp_start)]

    def to_timestamp_end_cmd(self) -> list[str]:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            Lista de strings lista para consumo de ffmpeg.
        """
        if self.timestamp_end is None:
            raise MissingParameterError(name="timestamp_end")
        return ["-to", str(self.timestamp_end)]


@dataclass(kw_only=True)
class TimestampAtMixin(_HasSingleMedia):
    """Mixin para listas de marcas de tiempo.

    Attributes:
        timestamp_at: Lista de marcas de tiempo.
    """

    timestamp_at: list[timedelta] | None = None

    def create_timestamp_at(self, times_str: str) -> None:
        """Parsea y valida un str de timestamp de marca de tiempo.

        Args:
            times_str: String de lista de marcas de tiempo.

        Raises:
            InvalidArgumentError: Si el str no tiene un formato válido.
        """
        times: list[timedelta] = []
        try:
            times_array = times_str.split(",")
        except ValueError as e:
            raise InvalidArgumentError(
                msg=_("Invalidad timestamp list format. Expected hh:mm:ss,hh:mm:ss,...")
            ) from e
        for time_str in times_array:
            time = _process_time(time_str=time_str, media=self.media)
            times.append(time)
        times.sort()
        self.timestamp_at = times


def _process_time(time_str: str, media: Media) -> timedelta:
    """Valida y procesa la marca de tiempo."""

    def _parse_to_timedelta() -> timedelta:
        """Convierte str ('hh:mm:ss', 'mm:ss', 'ss') a timedelta."""
        parts = time_str.split(":")
        if not parts:
            raise InvalidTimeFormatError()
        *measured, seconds = parts
        if not all(re.fullmatch(r"\d+", p) for p in measured):
            raise InvalidTimeFormatError()
        if not re.fullmatch(r"\d+(?:\.\d+)?", seconds):
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
            raise MissingMediaPropertyError(name="video.duration")
        if time_delta > media.duration:
            raise InvalidParameterError(
                _("Timestamp %(time)s exceeds video duration %(duration)s.")
                % {"time": str(time_delta), "duration": str(media.duration)}
            )

    time_delta = _parse_to_timedelta()
    _validate_time()

    return time_delta
