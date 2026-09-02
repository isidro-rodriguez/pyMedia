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
from pymedia.utils import parse_timedelta


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

    def create_timestamp_start(self, start: str) -> None:
        """Crea el atributo de marca de tiempo indicando el punto inicial.

        Args:
            start: String indicando punto inicial.

        Raises:
            InvalidTimeFormatError: Si el formato de la marca no es válido.
            MissingMediaPropertyError: Si no se pudo obtener la duración del vídeo.
            MissingParameterError: Si no se pudo obtener el parámetro.
            TimeExceedsDurationError: Si marca de tiempo superior a la duración.
        """
        self.timestamp_start = _process_time(time_str=start, media=self.media)

    def to_timestamp_start_cmd(self) -> list[str]:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            Lista de strings lista para consumo de ffmpeg.
        """
        if self.timestamp_start is None:
            raise MissingParameterError(name="timestamp_start")
        return ["-ss", str(self.timestamp_start)]

    def validate_timestamp_start_order(self, time: timedelta) -> None:
        """Comprueba que la marca de inicio sea anterior a la marca indicada.

        Args:
            time: Marca de tiempo (normalmente el final) con la que comparar.

        Raises:
            MissingParameterError: Si la marca de inicio no está definida.
            InvalidParameterError: Si la marca de inicio es posterior o igual.
        """
        if self.timestamp_start is None:
            raise MissingParameterError(name="timestamp_end")
        if self.timestamp_start >= time:
            raise InvalidParameterError(
                msg=_("Invalid timestamps. Start %(start)s >= %(time)s.")
                % {
                    "start": parse_timedelta(self.timestamp_start),
                    "time": parse_timedelta(time),
                }
            )


@dataclass(kw_only=True)
class TimestampEndMixin(_HasSingleMedia):
    """Mixin para las marcas de tiempo que indican el punto final a procesar.

    Attributes:
        timestamp_end: Marca de tiempo que indica el punto final.
    """

    timestamp_end: timedelta | None = None

    def create_timestamp_end(self, end: str) -> None:
        """Crea el atributo de marca de tiempo indicando el punto final.

        Args:
            end: String indicando punto final.

        Raises:
            InvalidTimeFormatError: Si el formato de la marca no es válido.
            MissingMediaPropertyError: Si no se pudo obtener la duración del vídeo.
            MissingParameterError: Si no se pudo obtener el parámetro.
            TimeExceedsDurationError: Si marca de tiempo superior a la duración.
        """
        self.timestamp_end = _process_time(time_str=end, media=self.media)

    def to_timestamp_end_cmd(self) -> list[str]:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            Lista de strings lista para consumo de ffmpeg.
        """
        if self.timestamp_end is None:
            raise MissingParameterError(name="timestamp_end")
        return ["-to", str(self.timestamp_end)]

    def validate_timestamp_end_order(self, time: timedelta) -> None:
        """Comprueba que la marca indicada sea anterior a la marca de fin.

        Args:
            time: Marca de tiempo (normalmente el inicio) con la que comparar.

        Raises:
            MissingParameterError: Si la marca de fin no está definida.
            InvalidParameterError: Si la marca de fin es anterior o igual.
        """
        if self.timestamp_end is None:
            raise MissingParameterError(name="timestamp_end")
        if time >= self.timestamp_end:
            raise InvalidParameterError(
                msg=_("Invalid timestamps. End %(time)s <= %(end)s.")
                % {
                    "time": parse_timedelta(time),
                    "end": parse_timedelta(self.timestamp_end),
                }
            )


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
