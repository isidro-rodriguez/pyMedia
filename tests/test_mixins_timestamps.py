"""Tests de mixins de marcas de tiempo (pymedia.models.mixins.timestamps_mixin)."""

from datetime import timedelta

import pytest

from pymedia.errors import (
    InvalidParameterError,
    InvalidTimeFormatError,
    MissingMediaPropertyError,
    MissingParameterError,
)
from pymedia.models.media import Media
from pymedia.models.mixins.timestamps_mixin import (
    TimestampStartEndMixin,
)


def _media(duration: timedelta | None = timedelta(hours=2)) -> Media:
    """Vídeo fuente con 2 horas de duración por defecto."""
    return Media(duration=duration)


class TestCreateTimestampStart:
    """Pruebas de creación de la marca de inicio."""

    @pytest.mark.parametrize(
        ("timestamp_start", "expected"),
        [
            ("5", timedelta(seconds=5)),
            ("01:30", timedelta(minutes=1, seconds=30)),
            ("01:02:03", timedelta(hours=1, minutes=2, seconds=3)),
        ],
    )
    def test_supported_formats(self, start, expected):
        """Comprueba que los formatos soportados se parsean correctamente."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media()

        mixin.create_timestamp_start(start=start)

        assert mixin.timestamp_start == expected

    @pytest.mark.parametrize("timestamp_start", ["abc", "", "1:2:3:4", "1.5:3", "3,5"])
    def test_invalid_format_raises(self, start):
        """Comprueba que los formatos inválidos lanzan un error."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media()

        with pytest.raises(InvalidTimeFormatError):
            mixin.create_timestamp_start(start=start)

    def test_missing_duration_raises(self):
        """Comprueba que la ausencia de duración lanza un error."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media(duration=None)

        with pytest.raises(MissingMediaPropertyError, match="duration"):
            mixin.create_timestamp_start(start="00:00:05")

    def test_exceeds_duration_raises(self):
        """Comprueba que una marca posterior a la duración lanza un error."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media(duration=timedelta(seconds=30))

        with pytest.raises(InvalidParameterError):
            mixin.create_timestamp_start(start="00:00:31")

    def test_equal_to_duration_is_allowed(self):
        """Comprueba que una marca igual a la duración es válida."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media(duration=timedelta(minutes=1))

        mixin.create_timestamp_start(start="00:01:00")

        assert mixin.timestamp_start == timedelta(minutes=1)


class TestCreateTimestampEnd:
    """Pruebas de creación de la marca de fin."""

    @pytest.mark.parametrize(
        ("timestamp_end", "expected"),
        [
            ("5", timedelta(seconds=5)),
            ("02:10", timedelta(minutes=2, seconds=10)),
            ("00:01:30", timedelta(minutes=1, seconds=30)),
        ],
    )
    def test_supported_formats(self, end, expected):
        """Comprueba que los formatos soportados se parsean correctamente."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media()

        mixin.create_timestamp_end(end=end)

        assert mixin.timestamp_end == expected

    @pytest.mark.parametrize("timestamp_end", ["", "-10", "1:2:3:4", "a:00"])
    def test_invalid_format_raises(self, end):
        """Comprueba que los formatos inválidos lanzan un error."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media()

        with pytest.raises(InvalidTimeFormatError):
            mixin.create_timestamp_end(end=end)

    def test_missing_duration_raises(self):
        """Comprueba que la ausencia de duración lanza un error."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media(duration=None)

        with pytest.raises(MissingMediaPropertyError, match="duration"):
            mixin.create_timestamp_end(end="00:00:05")

    def test_exceeds_duration_raises(self):
        """Comprueba que un fin posterior a la duración lanza un error."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media(duration=timedelta(minutes=5))

        with pytest.raises(InvalidParameterError):
            mixin.create_timestamp_end(end="00:06:00")


class TestToTimestampStartCmd:
    """Pruebas de generación del flag `-ss`."""

    def test_returns_ss_flag(self):
        """Comprueba que se genera el flag `-ss` con la marca formateada."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media()
        mixin.timestamp_start = timedelta(minutes=1, seconds=30)

        assert mixin.to_timestamp_start_cmd() == ["-ss", "0:01:30"]

    def test_missing_parameter_raises(self):
        """Comprueba que la ausencia de marca lanza un error."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media()
        mixin.timestamp_start = None

        with pytest.raises(MissingParameterError, match="timestamp_start"):
            mixin.to_timestamp_start_cmd()


class TestToTimestampEndCmd:
    """Pruebas de generación del flag `-to`."""

    def test_returns_to_flag(self):
        """Comprueba que se genera el flag `-to` con la marca formateada."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media()
        mixin.timestamp_end = timedelta(seconds=90)

        assert mixin.to_timestamp_end_cmd() == ["-to", "0:01:30"]

    def test_missing_parameter_raises(self):
        """Comprueba que la ausencia de marca lanza un error."""
        mixin = TimestampStartEndMixin()
        mixin.media = _media()
        mixin.timestamp_end = None

        with pytest.raises(MissingParameterError, match="timestamp_end"):
            mixin.to_timestamp_end_cmd()


@pytest.mark.parametrize(
    ("timestamp_start", "expected"),
    [
        ("5.5", timedelta(seconds=5.5)),
        ("01:30.5", timedelta(minutes=1, seconds=30.5)),
    ],
)
def test_fractional_seconds_should_be_allowed(start, expected):
    """Los segundos fraccionarios funcionan, como en ffmpeg."""
    mixin = TimestampStartEndMixin()
    mixin.media = _media(duration=timedelta(minutes=10))

    mixin.create_timestamp_start(start=start)

    assert mixin.timestamp_start == expected
