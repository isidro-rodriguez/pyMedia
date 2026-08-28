"""Tests de mixins de marcas de tiempo (pymedia.models.mixins.timestamps_mixin)."""

from datetime import timedelta

import pytest

from pymedia.errors import (
    InvalidTimeFormatError,
    MissingMediaPropertyError,
    MissingParameterError,
    TimeExceedsDurationError,
)
from pymedia.models.media import Media
from pymedia.models.mixins.timestamps_mixin import (
    TimestampEndMixin,
    TimestampStartMixin,
)


def _media(duration: timedelta | None = timedelta(hours=2)) -> Media:
    """Vídeo fuente con 2 horas de duración por defecto."""
    return Media(duration=duration)


class TestCreateTimestampStart:
    def test_none_sets_attr_none(self):
        mixin = TimestampStartMixin()
        mixin.media = _media()

        mixin.create_timestamp_start(start=None)

        assert mixin.timestamp_start is None

    @pytest.mark.parametrize(
        ("start", "expected"),
        [
            ("5", timedelta(seconds=5)),
            ("01:30", timedelta(minutes=1, seconds=30)),
            ("01:02:03", timedelta(hours=1, minutes=2, seconds=3)),
        ],
    )
    def test_supported_formats(self, start, expected):
        mixin = TimestampStartMixin()
        mixin.media = _media()

        mixin.create_timestamp_start(start=start)

        assert mixin.timestamp_start == expected

    @pytest.mark.parametrize("start", ["abc", "", "1:2:3:4", "1.5:3", "3,5"])
    def test_invalid_format_raises(self, start):
        mixin = TimestampStartMixin()
        mixin.media = _media()

        with pytest.raises(InvalidTimeFormatError):
            mixin.create_timestamp_start(start=start)

    def test_missing_duration_raises(self):
        mixin = TimestampStartMixin()
        mixin.media = _media(duration=None)

        with pytest.raises(MissingMediaPropertyError, match="duration"):
            mixin.create_timestamp_start(start="00:00:05")

    def test_exceeds_duration_raises(self):
        mixin = TimestampStartMixin()
        mixin.media = _media(duration=timedelta(seconds=30))

        with pytest.raises(TimeExceedsDurationError):
            mixin.create_timestamp_start(start="00:00:31")

    def test_equal_to_duration_is_allowed(self):
        mixin = TimestampStartMixin()
        mixin.media = _media(duration=timedelta(minutes=1))

        mixin.create_timestamp_start(start="00:01:00")

        assert mixin.timestamp_start == timedelta(minutes=1)


class TestCreateTimestampEnd:
    def test_none_sets_attr_none(self):
        mixin = TimestampEndMixin()
        mixin.media = _media()

        mixin.create_timestamp_end(end=None)

        assert mixin.timestamp_end is None

    @pytest.mark.parametrize(
        ("end", "expected"),
        [
            ("5", timedelta(seconds=5)),
            ("02:10", timedelta(minutes=2, seconds=10)),
            ("00:01:30", timedelta(minutes=1, seconds=30)),
        ],
    )
    def test_supported_formats(self, end, expected):
        mixin = TimestampEndMixin()
        mixin.media = _media()

        mixin.create_timestamp_end(end=end)

        assert mixin.timestamp_end == expected

    @pytest.mark.parametrize("end", ["", "-10", "1:2:3:4", "a:00"])
    def test_invalid_format_raises(self, end):
        mixin = TimestampEndMixin()
        mixin.media = _media()

        with pytest.raises(InvalidTimeFormatError):
            mixin.create_timestamp_end(end=end)

    def test_missing_duration_raises(self):
        mixin = TimestampEndMixin()
        mixin.media = _media(duration=None)

        with pytest.raises(MissingMediaPropertyError, match="duration"):
            mixin.create_timestamp_end(end="00:00:05")

    def test_exceeds_duration_raises(self):
        mixin = TimestampEndMixin()
        mixin.media = _media(duration=timedelta(minutes=5))

        with pytest.raises(TimeExceedsDurationError):
            mixin.create_timestamp_end(end="00:06:00")


class TestToTimestampStartCmd:
    def test_returns_ss_flag(self):
        mixin = TimestampStartMixin()
        mixin.media = _media()
        mixin.timestamp_start = timedelta(minutes=1, seconds=30)

        assert mixin.to_timestamp_start_cmd() == ["-ss", "0:01:30"]

    def test_missing_parameter_raises(self):
        mixin = TimestampStartMixin()
        mixin.media = _media()
        mixin.timestamp_start = None

        with pytest.raises(MissingParameterError, match="timestamp_start"):
            mixin.to_timestamp_start_cmd()


class TestToTimestampEndCmd:
    def test_returns_to_flag(self):
        mixin = TimestampEndMixin()
        mixin.media = _media()
        mixin.timestamp_end = timedelta(seconds=90)

        assert mixin.to_timestamp_end_cmd() == ["-to", "0:01:30"]

    def test_missing_parameter_raises(self):
        mixin = TimestampEndMixin()
        mixin.media = _media()
        mixin.timestamp_end = None

        with pytest.raises(MissingParameterError, match="timestamp_end"):
            mixin.to_timestamp_end_cmd()


@pytest.mark.parametrize(
    ("start", "expected"),
    [
        ("5.5", timedelta(seconds=5.5)),
        ("01:30.5", timedelta(minutes=1, seconds=30.5)),
    ],
)
def test_fractional_seconds_should_be_allowed(start, expected):
    """Los segundos fraccionarios funcionan, como en ffmpeg."""
    mixin = TimestampStartMixin()
    mixin.media = _media(duration=timedelta(minutes=10))

    mixin.create_timestamp_start(start=start)

    assert mixin.timestamp_start == expected
