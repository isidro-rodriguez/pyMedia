"""Tests de utilidades de parseo y formateo (pymedia.utils)."""

from datetime import timedelta
from fractions import Fraction
from pathlib import Path

import pytest

from pymedia.utils import (
    parse_fraction,
    parse_quantity,
    parse_size,
    parse_timedelta,
    to_ffmpeg_path,
    to_float,
    to_int,
)


class TestParseFraction:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("25/1", Fraction(25, 1)),
            ("30000/1001", Fraction(30000, 1001)),
            ("-1/2", Fraction(-1, 2)),
        ],
    )
    def test_valid_values(self, value, expected):
        assert parse_fraction(value) == expected

    @pytest.mark.parametrize("value", ["", "0/0", "abc", "30", "25/0"])
    def test_invalid_values_are_none(self, value):
        assert parse_fraction(value) is None

    def test_none_is_none(self):
        assert parse_fraction(None) is None


class TestParseQuantity:
    @pytest.mark.parametrize(
        ("value", "locale", "expected"),
        [
            (1_000, "es", "1.000"),
            (1_234_567, "es", "1.234.567"),
            (1_234_567, "en", "1,234,567"),
            (5, "es", "5"),
            (5, "en", "5"),
        ],
    )
    def test_int(self, value, locale, expected):
        assert parse_quantity(value, locale) == expected

    @pytest.mark.parametrize(
        ("value", "locale", "expected"),
        [
            (1_234_567.891, "es", "1.234.567,891"),
            (1_234_567.891, "en", "1,234,567.891"),
            (1234.5, "en", "1,234.500"),
        ],
    )
    def test_float(self, value, locale, expected):
        assert parse_quantity(value, locale) == expected

    @pytest.mark.parametrize(
        ("value", "locale", "expected"),
        [
            (Fraction(3, 2), "es", "1,500"),
            (Fraction(5, 1), "es", "5"),
            (Fraction(3, 2), "en", "1.500"),
        ],
    )
    def test_fraction(self, value, locale, expected):
        assert parse_quantity(value, locale) == expected


class TestParseSize:
    def test_lower_than_gib_appears_in_mb(self):
        assert parse_size(5, "es") == "0,000 MB (5 bytes)"

    def test_exactly_one_gib_stays_in_mb(self):
        # El umbral es `>` estricto: con 1 GiB exacto no salta a GB.
        assert parse_size(1024**3, "es") == "1.024,000 MB (1.073.741.824 bytes)"

    def test_greater_than_gib_appears_in_gb(self):
        assert parse_size(1024**3 + 1, "es") == ("1,000 GB (1.073.741.825 bytes)")

    def test_en_locale(self):
        assert parse_size(5, "en") == "0.000 MB (5 bytes)"


class TestParseTimedelta:
    @pytest.mark.parametrize(
        ("time", "expected"),
        [
            (timedelta(hours=2, minutes=1), "2:01:00"),
            (timedelta(minutes=1, seconds=30), "1:30"),
            (timedelta(seconds=90), "1:30"),
            (timedelta(), "0:00"),
            (timedelta(seconds=0), "0:00"),
        ],
    )
    def test_formats(self, time, expected):
        assert parse_timedelta(time) == expected


class TestToFfmpegPath:
    def test_posix_path_unchanged(self):
        assert (
            to_ffmpeg_path(Path("src/resources/font.ttf")) == "src/resources/font.ttf"
        )

    def test_windows_drive_colon_escaped(self):
        assert (
            to_ffmpeg_path(Path("C:/Users/test/data.ttf")) == "C\\:/Users/test/data.ttf"
        )


class TestToFloat:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [("3.5", 3.5), ("0", 0.0), (3, 3.0), ("-2.25", -2.25)],
    )
    def test_valid_values(self, value, expected):
        assert to_float(value) == expected

    @pytest.mark.parametrize("value", ["", "abc", "3,5"])
    def test_invalid_values_are_none(self, value):
        assert to_float(value) is None

    def test_none_is_none(self):
        assert to_float(None) is None


class TestToInt:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [("25", 25), ("0", 0), (25, 25), ("-5", -5)],
    )
    def test_valid_values(self, value, expected):
        assert to_int(value) == expected

    @pytest.mark.parametrize("value", ["", "abc", "25.5"])
    def test_invalid_values_are_none(self, value):
        assert to_int(value) is None

    def test_none_is_none(self):
        assert to_int(None) is None
