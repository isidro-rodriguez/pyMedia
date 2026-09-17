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
    to_ffmpeg_value,
    to_float,
    to_int,
)


def _unescape_filter_value(value: str) -> str:
    r"""Revierte un nivel de escape de ffmpeg: `\X` se lee como `X`."""
    out: list[str] = []
    index = 0
    while index < len(value):
        if value[index] == "\\":
            index += 1
        out.append(value[index])
        index += 1
    return "".join(out)


class TestParseFraction:
    """Pruebas de `parse_fraction`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("25/1", Fraction(25, 1)),
            ("30000/1001", Fraction(30000, 1001)),
            ("-1/2", Fraction(-1, 2)),
        ],
    )
    def test_valid_values(self, value: str, expected: Fraction) -> None:
        """Comprueba que las fracciones válidas se parsean correctamente."""
        assert parse_fraction(value) == expected

    @pytest.mark.parametrize("value", ["", "0/0", "abc", "30", "25/0"])
    def test_invalid_values_are_none(self, value: str) -> None:
        """Comprueba que los valores inválidos devuelven `None`."""
        assert parse_fraction(value) is None

    def test_none_is_none(self) -> None:
        """Comprueba que `None` devuelve `None`."""
        assert parse_fraction(None) is None


class TestParseQuantity:
    """Pruebas de `parse_quantity`."""

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
    def test_int(self, value: int, locale: str, expected: str) -> None:
        """Comprueba el formateo de enteros con el separador del locale."""
        assert parse_quantity(value, locale) == expected

    @pytest.mark.parametrize(
        ("value", "locale", "expected"),
        [
            (1_234_567.891, "es", "1.234.567,891"),
            (1_234_567.891, "en", "1,234,567.891"),
            (1234.5, "en", "1,234.500"),
        ],
    )
    def test_float(self, value: float, locale: str, expected: str) -> None:
        """Comprueba el formateo de flotantes con tres decimales."""
        assert parse_quantity(value, locale) == expected

    @pytest.mark.parametrize(
        ("value", "locale", "expected"),
        [
            (Fraction(3, 2), "es", "1,500"),
            (Fraction(5, 1), "es", "5"),
            (Fraction(3, 2), "en", "1.500"),
        ],
    )
    def test_fraction(self, value: Fraction, locale: str, expected: str) -> None:
        """Comprueba el formateo de fracciones según el locale."""
        assert parse_quantity(value, locale) == expected


class TestParseSize:
    """Pruebas de `parse_size`."""

    def test_lower_than_gib_appears_in_mb(self) -> None:
        """Comprueba que los tamaños menores a 1 GiB se muestran en MB."""
        assert parse_size(5, "es") == "0,000 MB (5 bytes)"

    def test_exactly_one_gib_stays_in_mb(self) -> None:
        """Comprueba que 1 GiB exacto se mantiene en MB."""
        # El umbral es `>` estricto: con 1 GiB exacto no salta a GB.
        assert parse_size(1024**3, "es") == "1.024,000 MB (1.073.741.824 bytes)"

    def test_greater_than_gib_appears_in_gb(self) -> None:
        """Comprueba que los tamaños mayores a 1 GiB se muestran en GB."""
        assert parse_size(1024**3 + 1, "es") == ("1,000 GB (1.073.741.825 bytes)")

    def test_en_locale(self) -> None:
        """Comprueba el formateo con separadores de inglés."""
        assert parse_size(5, "en") == "0.000 MB (5 bytes)"


class TestParseTimedelta:
    """Pruebas de `parse_timedelta`."""

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
    def test_formats(self, time: timedelta, expected: str) -> None:
        """Comprueba el formato de salida según la duración."""
        assert parse_timedelta(time) == expected


class TestToFfmpegValue:
    """Pruebas de `to_ffmpeg_value`."""

    def test_path_without_metacharacters_unchanged(self) -> None:
        """Comprueba que una ruta sin metacaracteres no se modifica."""
        assert (
            to_ffmpeg_value(Path("src/resources/font.ttf")) == "src/resources/font.ttf"
        )

    @pytest.mark.parametrize(
        ("path", "expected"),
        [
            ("C:/Users/test/data.ttf", r"C\\\:/Users/test/data.ttf"),
            ("mi fichero.mp4", r"mi\\\ fichero.mp4"),
            (
                "Joan's first bycicle, [2].srt",
                r"Joan\\\'s\\\ first\\\ bycicle\\\,\\\ \\\[2\\\].srt",
            ),
        ],
    )
    def test_metacharacters_escaped(self, path: str, expected: str) -> None:
        """Comprueba que los metacaracteres se escapan en los dos niveles."""
        assert to_ffmpeg_value(Path(path)) == expected

    @pytest.mark.parametrize(
        "path",
        ["subs/eng_subs.srt", "mi fichero.mp4", "Joan's first bycicle, [2].srt"],
    )
    def test_round_trip_decodes_to_the_original_path(self, path: str) -> None:
        """Comprueba que tras desescapar dos veces se obtiene la ruta original."""
        escaped = to_ffmpeg_value(Path(path))

        assert _unescape_filter_value(_unescape_filter_value(escaped)) == path

    def test_value_is_not_quoted(self) -> None:
        """Comprueba que el valor no se entrecomilla: ffmpeg no anida comillas."""
        assert '"' not in to_ffmpeg_value(Path("Joan's first bycicle.mp4"))


class TestToFloat:
    """Pruebas de `to_float`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("3.5", 3.5), ("0", 0.0), (3, 3.0), ("-2.25", -2.25)],
    )
    def test_valid_values(self, value: str | int, expected: float) -> None:
        """Comprueba que los valores numéricos se convierten a float."""
        assert to_float(value) == expected

    @pytest.mark.parametrize("value", ["", "abc", "3,5"])
    def test_invalid_values_are_none(self, value: str) -> None:
        """Comprueba que los valores inválidos devuelven `None`."""
        assert to_float(value) is None

    def test_none_is_none(self) -> None:
        """Comprueba que `None` devuelve `None`."""
        assert to_float(None) is None


class TestToInt:
    """Pruebas de `to_int`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [("25", 25), ("0", 0), (25, 25), ("-5", -5)],
    )
    def test_valid_values(self, value: str | int, expected: int) -> None:
        """Comprueba que los valores numéricos se convierten a int."""
        assert to_int(value) == expected

    @pytest.mark.parametrize("value", ["", "abc", "25.5"])
    def test_invalid_values_are_none(self, value: str) -> None:
        """Comprueba que los valores inválidos devuelven `None`."""
        assert to_int(value) is None

    def test_none_is_none(self) -> None:
        """Comprueba que `None` devuelve `None`."""
        assert to_int(None) is None
