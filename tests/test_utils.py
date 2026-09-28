"""Tests de utilidades de parseo y formateo (pymedia.utils)."""

from datetime import timedelta
from fractions import Fraction
from pathlib import Path

import pytest

from pymedia.utils import (
    parse_date,
    parse_duration,
    parse_fraction,
    parse_quantity,
    parse_r128_gain,
    parse_replaygain_gain,
    parse_size,
    parse_timedelta,
    ticks_to_timedelta,
    to_bool,
    to_dict,
    to_dict_list,
    to_ffmpeg_value,
    to_float,
    to_int,
    to_text,
    to_timedelta,
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


class TestParseDate:
    """Pruebas de `pymedia.utils.parse_date`."""

    @pytest.mark.parametrize(
        ("raw", "year", "month", "day"),
        [
            # ISO 8601 con Z
            ("2024-01-15T12:00:00Z", 2024, 1, 15),
            ("2024-01-15T12:00:00+00:00", 2024, 1, 15),
            ("2024-06-30", 2024, 6, 30),
            ("2024-12-31T23:59:59", 2024, 12, 31),
            # RFC 2822 / RFC 5322
            ("Wed, 15 Jan 2024 12:00:00 +0000", 2024, 1, 15),
            ("Wed, 15 Jan 2024 12:00:00 GMT", 2024, 1, 15),
            # Nombres de mes (cortos y largos)
            ("Mon Jan 15 12:00:00 2024", 2024, 1, 15),
            ("Jan 15 12:00:00 2024", 2024, 1, 15),
            ("Jan 15 2024", 2024, 1, 15),
            ("15 Jan 2024", 2024, 1, 15),
            ("15 January 2024", 2024, 1, 15),
            ("January 15 2024", 2024, 1, 15),
            # Formatos numéricos no ISO
            ("2024/01/15", 2024, 1, 15),
            ("2024.01.15", 2024, 1, 15),
            ("15-01-2024", 2024, 1, 15),
            ("15/01/2024", 2024, 1, 15),
            ("15.01.2024", 2024, 1, 15),
            # Unix timestamp en segundos
            ("1705315200", 2024, 1, 15),
        ],
    )
    def test_valid_dates_return_midnight_utc(
        self, raw: str, year: int, month: int, day: int
    ) -> None:
        """Comprueba que las fechas válidas se parsean a medianoche UTC."""
        from datetime import datetime

        result = parse_date(raw)

        assert result is not None
        assert result == datetime(year, month, day)

    @pytest.mark.parametrize(
        "raw",
        [
            "",
            "not-a-date",
            "2024-13-01",
            "2024-02-30",
            "2024-02-31",
            "2024-00-01",
            "12/31/2024",
            "32/01/2024",
            "2024/13/01",
            "2024/00/01",
            "2024-01-32",
            "31 Feb 2024",
        ],
    )
    def test_invalid_dates_return_none(self, raw: str) -> None:
        """Comprueba que las fechas inválidas o ambiguas devuelven None."""
        assert parse_date(raw) is None

    def test_none_returns_none(self) -> None:
        """Comprueba que `None` devuelve `None`."""
        assert parse_date(None) is None

    def test_empty_string_returns_none(self) -> None:
        """Comprueba que una cadena vacía devuelve `None`."""
        assert parse_date("") is None


class TestParseDuration:
    """Pruebas de `parse_duration`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("01:02:03.456", timedelta(hours=1, minutes=2, seconds=3.456)),
            ("00:00:01", timedelta(seconds=1)),
            ("123.45", timedelta(seconds=123.45)),
            ("42", timedelta(seconds=42)),
            ("0", timedelta(0)),
            ("  02:03:04.005  ", timedelta(hours=2, minutes=3, seconds=4.005)),
        ],
    )
    def test_valid_values(self, value: str, expected: timedelta) -> None:
        """Comprueba que las duraciones válidas se parsean correctamente."""
        assert parse_duration(value) == expected

    @pytest.mark.parametrize(
        "value",
        [
            123,
            None,
            "",
            "abcd",
            "12:34",  # missing seconds?
            "12:34:56.78.90",  # extra dot
            "-01:00:00",
            "-5.5",
            "1e13",  # exceeds _MAX_SECONDS
        ],
    )
    def test_invalid_values_are_none(self, value: object) -> None:
        """Comprueba que los valores inválidos devuelven `None`."""
        assert parse_duration(value) is None


class TestParseR128Gain:
    """Pruebas de `parse_r128_gain`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("0", -23.0),
            ("256", -22.0),
            ("-256", -24.0),
            ("128", -22.5),
        ],
    )
    def test_valid_values(self, value: str, expected: float) -> None:
        """Comprueba que los valores de ganancia válidos se convierten correctamente."""
        assert parse_r128_gain(value) == expected

    @pytest.mark.parametrize(
        "value",
        [
            "",
            None,
            "abc",
        ],
    )
    def test_invalid_values_are_none(self, value: str | None) -> None:
        """Comprueba que los valores inválidos devuelven `None`."""
        assert parse_r128_gain(value) is None


class TestParseReplaygainGain:
    """Pruebas de `parse_replaygain_gain`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("-3.50 dB", -3.5),
            ("3.5", 3.5),
            ("  -3.50 dB  ", -3.5),
            ("0", 0.0),
            ("-0.0", 0.0),
        ],
    )
    def test_valid_values(self, value: str, expected: float) -> None:
        """Comprueba que la ganancia ReplayGain válidos se convierten correctamente."""
        assert parse_replaygain_gain(value) == expected

    @pytest.mark.parametrize(
        "value",
        [
            "",
            None,
            "abc dB",
            "abc",
        ],
    )
    def test_invalid_values_are_none(self, value: str | None) -> None:
        """Comprueba que los valores inválidos devuelven `None`."""
        assert parse_replaygain_gain(value) is None


class TestTicksToTimedelta:
    """Pruebas de `ticks_to_timedelta`."""

    @pytest.mark.parametrize(
        ("ticks", "time_base", "expected"),
        [
            ("1000", Fraction(1, 1000), timedelta(seconds=1)),
            ("0", Fraction(1, 1000), timedelta(0)),
            ("-500", Fraction(1, 1000), timedelta(seconds=-0.5)),
            ("10", Fraction(1, 1), timedelta(seconds=10)),
        ],
    )
    def test_valid_values(
        self, ticks: str | int, time_base: Fraction, expected: timedelta
    ) -> None:
        """Comprueba que los valores válidos se convierten correctamente."""
        assert ticks_to_timedelta(ticks, time_base) == expected

    @pytest.mark.parametrize(
        ("ticks", "time_base"),
        [
            ("abc", Fraction(1, 1000)),
            (None, Fraction(1, 1000)),
            ("10", None),
        ],
    )
    def test_invalid_values_are_none(
        self, ticks: str | int | None, time_base: Fraction | None
    ) -> None:
        """Comprueba que los valores inválidos devuelven `None`."""
        assert ticks_to_timedelta(ticks, time_base) is None

    def test_large_product_exceeds_max(self) -> None:
        """Comprueba que un producto demasiado grande devuelve None."""
        # _MAX_SECONDS = 1e12
        large_ticks = 10**15
        time_base = Fraction(1, 1)
        assert ticks_to_timedelta(large_ticks, time_base) is None


class TestToBool:
    """Pruebas de `to_bool`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("1", True),
            ("0", False),
            (1, True),
            (0, False),
            (-1, True),
            ("-5", True),
            ("", False),
            (None, False),
            ("abc", False),
        ],
    )
    def test_values(self, value: str | int | None, expected: bool) -> None:
        """Comprueba la conversión a booleano."""
        assert to_bool(value) == expected


class TestToDict:
    """Pruebas de `to_dict`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ({"a": 1}, {"a": 1}),
            ({}, {}),
            ([], {}),
            ("", {}),
            (None, {}),
            (123, {}),
        ],
    )
    def test_values(self, value: object, expected: dict[str, object]) -> None:
        """Comprueba que se devuelve el diccionario o uno vacío."""
        assert to_dict(value) == expected


class TestToDictList:
    """Pruebas de `to_dict_list`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ([{"a": 1}, {"b": 2}], [{"a": 1}, {"b": 2}]),
            ([{"a": 1}, "b", 2], [{"a": 1}]),
            ([], []),
            (None, []),
            ("", []),
            (123, []),
        ],
    )
    def test_values(self, value: object, expected: list[dict[str, object]]) -> None:
        """Comprueba que se devuelven los diccionarios de la lista o una lista vacía."""
        assert to_dict_list(value) == expected


class TestToText:
    """Pruebas de `to_text`."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("hola", "hola"),
            (" ", " "),
            ("", None),
            (None, None),
            (123, None),
            ([], None),
        ],
    )
    def test_values(self, value: object, expected: str | None) -> None:
        """Comprueba que se devuelve el texto no vacío o None."""
        assert to_text(value) == expected


class TestToTimedelta:
    """Pruebas de `to_timedelta`."""

    @pytest.mark.parametrize(
        ("seconds", "expected"),
        [
            (1.5, timedelta(seconds=1.5)),
            (0, timedelta(0)),
            (-2.5, timedelta(seconds=-2.5)),
        ],
    )
    def test_valid_values(self, seconds: float | None, expected: timedelta) -> None:
        """Comprueba que los valores válidos se convierten correctamente."""
        assert to_timedelta(seconds) == expected

    @pytest.mark.parametrize(
        "seconds",
        [
            None,
            float("inf"),
            float("-inf"),
            float("nan"),
        ],
    )
    def test_non_finite_returns_none(self, seconds: float | None) -> None:
        """Comprueba that the non-finite values return None."""
        assert to_timedelta(seconds) is None

    def test_exceeds_max_returns_none(self) -> None:
        """Comprueba que un valor demasiado grande devuelve `None`."""
        # _MAX_SECONDS = 1e12
        assert to_timedelta(1e13) is None
