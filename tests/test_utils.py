"""Tests de los helpers de conversión en utils.py."""

from fractions import Fraction

import pytest

from pymedia.utils import parse_fraction, to_float, to_int

# ─────────────────────── parse_fraction ─────────────────────


@pytest.mark.parametrize(
    "value, expected",
    [
        ("30/1", Fraction(30, 1)),
        ("25/1", Fraction(25, 1)),
        ("24000/1001", Fraction(24000, 1001)),
        ("60/1", Fraction(60, 1)),
    ],
)
def test_parse_fraction_valid(value: str, expected: Fraction) -> None:
    """Fracciones válidas se convierten correctamente."""
    assert parse_fraction(value) == expected


def test_parse_fraction_zero_zero() -> None:
    """'0/0' devuelve None (fps de audio sin framerate)."""
    assert parse_fraction("0/0") is None


def test_parse_fraction_none() -> None:
    """None devuelve None."""
    assert parse_fraction(None) is None


def test_parse_fraction_empty() -> None:
    """String vacío devuelve None."""
    assert parse_fraction("") is None


@pytest.mark.parametrize("value", ["abc", "25/", "/1", "abc/def"])
def test_parse_fraction_invalid(value: str) -> None:
    """Strings no parseables devuelven None."""
    assert parse_fraction(value) is None


# ─────────────────────── to_int ────────────────────────────


@pytest.mark.parametrize(
    "value, expected",
    [
        ("48000", 48000),
        ("44100", 44100),
        ("128000", 128000),
        (48000, 48000),
        ("0", 0),
    ],
)
def test_to_int_valid(value: str | int, expected: int) -> None:
    """Valores numéricos se convierten a int."""
    assert to_int(value) == expected


def test_to_int_none() -> None:
    """None devuelve None."""
    assert to_int(None) is None


@pytest.mark.parametrize("value", ["abc", "48.000", "", "12.5"])
def test_to_int_invalid(value: str) -> None:
    """Strings no numéricos devuelven None."""
    assert to_int(value) is None


# ─────────────────────── to_float ───────────────────────────


@pytest.mark.parametrize(
    "value, expected",
    [
        ("25.000000", 25.0),
        ("3.0", 3.0),
        ("0.5", 0.5),
        (25.0, 25.0),
        ("0", 0.0),
    ],
)
def test_to_float_valid(value: str | float, expected: float) -> None:
    """Valores numéricos se convierten a float."""
    assert to_float(value) == expected


def test_to_float_none() -> None:
    """None devuelve None."""
    assert to_float(None) is None


@pytest.mark.parametrize("value", ["abc", "", "not_a_number"])
def test_to_float_invalid(value: str) -> None:
    """Strings no numéricos devuelven None."""
    assert to_float(value) is None
