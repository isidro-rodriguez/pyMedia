"""Tests para las utilidades (pymedia.utils)."""

from datetime import timedelta
from fractions import Fraction
from pathlib import Path

from pymedia.utils import (
    convert_to_timedelta,
    parse_crop,
    parse_fraction,
    resolve_output_path,
    to_float,
    to_int,
)

# -----------------------------------------------------------------------------
#  parse_fraction()
# -----------------------------------------------------------------------------


def test_parse_fraction_valid():
    assert parse_fraction("25/1") == Fraction(25, 1)


def test_parse_fraction_none():
    assert parse_fraction(None) is None


def test_parse_fraction_zero_over_zero():
    assert parse_fraction("0/0") is None


def test_parse_fraction_not_numeric():
    assert parse_fraction("abc") is None


def test_parse_fraction_division_by_zero():
    assert parse_fraction("5/0") is None


# -----------------------------------------------------------------------------
#  to_int()
# -----------------------------------------------------------------------------


def test_to_int_string():
    assert to_int("42") == 42


def test_to_int_already_int():
    assert to_int(42) == 42


def test_to_int_none():
    assert to_int(None) is None


def test_to_int_invalid():
    assert to_int("abc") is None


# -----------------------------------------------------------------------------
#  to_float()
# -----------------------------------------------------------------------------


def test_to_float_string():
    assert to_float("3.14") == 3.14


def test_to_float_already_float():
    assert to_float(3.14) == 3.14


def test_to_float_none():
    assert to_float(None) is None


def test_to_float_invalid():
    assert to_float("abc") is None


# -----------------------------------------------------------------------------
#  parse_crop()
# -----------------------------------------------------------------------------


def test_parse_crop_valid():
    assert parse_crop("10,20,30,40") == (10, 20, 30, 40)


def test_parse_crop_none():
    assert parse_crop(None) is None


def test_parse_crop_wrong_number_of_values():
    assert parse_crop("1,2,3") is None


def test_parse_crop_negative_value():
    assert parse_crop("1,-2,3,4") is None


def test_parse_crop_not_numeric():
    assert parse_crop("a,b,c,d") is None


# -----------------------------------------------------------------------------
#  convert_to_timedelta()
# -----------------------------------------------------------------------------


def test_convert_to_timedelta_hms():
    assert convert_to_timedelta("1:30:00") == timedelta(hours=1, minutes=30)


def test_convert_to_timedelta_ms():
    assert convert_to_timedelta("1:30") == timedelta(minutes=1, seconds=30)


def test_convert_to_timedelta_s():
    assert convert_to_timedelta("45") == timedelta(seconds=45)


def test_convert_to_timedelta_negative():
    assert convert_to_timedelta("-1:00") == -timedelta(minutes=1)


def test_convert_to_timedelta_invalid():
    assert convert_to_timedelta("abc") is None


def test_convert_to_timedelta_too_many_parts():
    assert convert_to_timedelta("1:2:3:4") is None


# -----------------------------------------------------------------------------
#  resolve_output_path()
# -----------------------------------------------------------------------------


def test_resolve_output_path_default_name():
    result = resolve_output_path(Path("video.mp4"))
    assert result == Path("video_processed.mp4")


def test_resolve_output_path_custom_suffix():
    result = resolve_output_path(Path("video.mp4"), suffix="out")
    assert result == Path("video_out.mp4")


def test_resolve_output_path_explicit_name():
    result = resolve_output_path(Path("video.mp4"), output_name="out.mp4")
    assert result == Path("out.mp4")


def test_resolve_output_path_creates_parent(tmp_path):
    target = tmp_path / "sub" / "out.mp4"
    result = resolve_output_path(Path("video.mp4"), output_name=str(target))
    assert result == target
    assert target.parent.exists()