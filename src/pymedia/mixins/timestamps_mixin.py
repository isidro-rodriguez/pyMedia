"""Mixins de marcas de tiempo de inicio, fin y listas de marcas."""

import re
from dataclasses import dataclass
from datetime import timedelta

from pymedia.errors import (
    MissingParameterError,
    MissingPropertyError,
    UserError,
)
from pymedia.locales import _
from pymedia.models.media import Media


@dataclass(kw_only=True)
class TimestampStartEndMixin:
    """Mixin para las marcas de tiempo que indican el punto inicial a procesar.

    Attributes:
        timestamp_start: Marca de tiempo que indica el punto inicial.
    """

    media: Media | None = None
    timestamp_start: timedelta | None = None
    timestamp_end: timedelta | None = None

    def create_timestamp_start_end(
        self,
        timestamp_start: str | None,
        timestamp_end: str | None,
    ) -> None:
        """Crea el atributo de marca de tiempo indicando el punto inicial.

        Args:
            timestamp_start: Marca de tiempo que indica el punto inicial.
            timestamp_end: Marca de tiempo que indica el punto final.

        Raises:
            InvalidTimeFormatError: Si el formato de la marca no es válido.
            InvalidParameterError: Si la marca de inicio es posterior a la
                de fin.
            MissingPropertyError: Si no se pudo obtener la duración del vídeo.
            MissingParameterError: Si no se pudo obtener el parámetro.
        """
        media = self.media
        if media is None:
            raise MissingParameterError(name="media")

        if timestamp_start is not None:
            self.timestamp_start = _process_time(
                time_str=timestamp_start,
                media=media,
            )

        if timestamp_end is not None:
            self.timestamp_end = _process_time(
                time_str=timestamp_end,
                media=media,
            )

        if self.timestamp_start is not None and self.timestamp_end is not None:
            if self.timestamp_start > self.timestamp_end:
                raise UserError(
                    msg=_("Invalid timestamps. Start (%(start)s) >= End (%(end)s).")
                    % {"start": timestamp_start, "end": timestamp_end}
                )

    def to_timestamp_start_cmd(self) -> list[str]:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            Lista de argumentos `-ss <marca>`.

        Raises:
            MissingParameterError: Si no se ha definido `timestamp_start`.
        """
        if self.timestamp_start is None:
            raise MissingParameterError(name="timestamp_start")
        return ["-ss", str(self.timestamp_start)]

    def to_timestamp_end_cmd(self) -> list[str]:
        """Devuelve el filtro listo para consumo de ffmpeg.

        Returns:
            Lista de argumentos `-to <marca>`.

        Raises:
            MissingParameterError: Si no se ha definido `timestamp_end`.
        """
        if self.timestamp_end is None:
            raise MissingParameterError(name="timestamp_end")
        return ["-to", str(self.timestamp_end)]

    def get_range_time(self) -> timedelta:
        """Resuelve la duración del tramo de vídeo a procesar.

        Calcula la duración del tramo de vídeo a procesar definido por los flags
        `--start`, `--end` y `media.duration` para que muestre correctamente el avance
        la barra de progreso de Rich.

        Returns:
            Duración del tramo de vídeo a procesar.

        Raises:
            MissingPropertyError: Si `media.duration` no se pudo obtener.
        """
        media = self.media
        if media is None:
            raise MissingParameterError(name="media")
        media_duration = media.duration
        start, end = self.timestamp_start, self.timestamp_end

        if media_duration is None:
            raise MissingPropertyError(name="duration")
        if start is not None and end is not None:
            return end - start
        if start is not None:
            return media_duration - start
        if end is not None:
            return media_duration - end
        return media_duration


@dataclass(kw_only=True)
class TimestampAtMixin:
    """Mixin para listas de marcas de tiempo.

    Attributes:
        timestamp_at: Lista de marcas de tiempo.
    """

    media: Media | None = None
    timestamp_at: list[timedelta] | None = None

    def create_timestamp_at(self, times_str: str | None) -> None:
        """Parsea y valida un str de timestamp de marca de tiempo.

        Args:
            times_str: String de lista de marcas de tiempo.

        Raises:
            InvalidArgumentError: Si el str no tiene un formato válido.
            InvalidTimeFormatError: Si el formato de la marca no es válido.
            InvalidParameterError: Si la marca supera la duración del vídeo.
            MissingPropertyError: Si no se pudo obtener la duración del vídeo.
        """
        if times_str is None:
            return

        media = self.media
        if media is None:
            raise MissingParameterError(name="media")

        times: list[timedelta] = []
        for time_str in times_str.split(","):
            time = _process_time(time_str=time_str, media=media)
            if time in times:
                raise UserError(
                    msg=_("Time %(time)s is a duplicated timestamp.") % {"time": time}
                )
            for t in times:
                if time < t:
                    raise UserError(
                        _("The list of timestamps must be in ascending order.")
                    )
            times.append(time)

        self.timestamp_at = times

    def to_timestamp_at_cmd(self) -> list[str]:
        """Devuelve la lista de argumentos ffmpeg necesarias para indicar los cortes."""
        if self.timestamp_at is None:
            raise MissingParameterError(name="timestamp_at")

        times_str = ",".join(str(t) for t in self.timestamp_at)

        return ["-f", "segment", "-segment_times", times_str, "-reset_timestamps", "1"]


def _process_time(time_str: str, media: Media) -> timedelta:
    """Valida y procesa la marca de tiempo."""

    def _parse_to_timedelta() -> timedelta:
        """Convierte str ('hh:mm:ss', 'mm:ss', 'ss') a timedelta."""
        parts = time_str.split(":")
        message = _("Invalid timestamp format. Expected: hh:mm:ss.")
        if not parts:
            raise UserError(msg=message)
        *measured, seconds = parts
        if not all(re.fullmatch(r"\d+", p) for p in measured):
            raise UserError(msg=message)
        if not re.fullmatch(r"\d+(?:\.\d+)?", seconds):
            raise UserError(msg=message)
        match tuple(map(float, parts)):
            case (hours, minutes, secs):
                return timedelta(hours=hours, minutes=minutes, seconds=secs)
            case (minutes, secs):
                return timedelta(minutes=minutes, seconds=secs)
            case (secs,):
                return timedelta(seconds=secs)
            case _:
                raise UserError(msg=message)

    def _validate_time() -> None:
        """Valida que la marca de tiempo no supere la duración del vídeo."""
        if media.duration is None:
            raise MissingPropertyError(name="video.duration")
        if time_delta >= media.duration:
            raise UserError(
                _("Timestamp %(time)s exceeds video duration %(duration)s.")
                % {"time": str(time_delta), "duration": str(media.duration)}
            )

    time_delta = _parse_to_timedelta()
    _validate_time()

    return time_delta
