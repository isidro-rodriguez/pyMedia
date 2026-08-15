"""Tests para verificar la coherencia de los locales en src/pymedia/locales/.

A partir del locale base inglés (en), se comprueba que los demás locales
presenten los mismos dicts, las mismas llaves y los mismos parámetros.
También se verifica que ningún locale tenga llaves vacías, valores vacíos
o nulos, tipos incorrectos o parámetros duplicados.
"""

import importlib
import inspect
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from pymedia.services.locale_service import SUPPORTED_LANGUAGES

BASE_LOCALE = "en"
OTHER_LOCALES = sorted(SUPPORTED_LANGUAGES - {BASE_LOCALE})
EXPECTED_DICTS = (
    "Cli",
    "ConfigValidation",
    "Debug",
    "ExecutionError",
    "Info",
    "PipelineError",
    "Progress",
    "ValidationError",
    "Warnings",
)

SRC_DIR = Path(__file__).parent.parent.parent / "src" / "pymedia"
LOCALES_DIR = SRC_DIR / "locales"


def _load_locale(lang: str):
    """Importa dinámicamente el módulo de idioma indicado."""
    return importlib.import_module(f"pymedia.locales.{lang}")


def _extract_params(message: str) -> set:
    """Extrae los nombres de parámetros {name} de un mensaje."""
    return set(re.findall(r"\{(\w+)\}", message))


def _validate_locale_structure(locale, lang: str) -> None:
    """Valida la estructura interna de un locale (tipos, llaves y valores)."""
    for dict_name in EXPECTED_DICTS:
        data = getattr(locale, dict_name)
        assert isinstance(data, dict), f"{lang}: {dict_name} should be a dict"

        for key, value in data.items():
            assert isinstance(key, str), f"{lang}: {dict_name} key '{key}' should be str"
            assert key != "", f"{lang}: {dict_name} has an empty key"
            assert isinstance(value, str), f"{lang}: {dict_name}['{key}'] should be str"
            assert value != "", f"{lang}: {dict_name}['{key}'] is empty"
            assert value is not None, f"{lang}: {dict_name}['{key}'] is None"

            params = _extract_params(value)
            assert len(params) == len(re.findall(r"\{(\w+)\}", value)), \
                f"{lang}: {dict_name}['{key}'] has duplicated params: {value}"


def _iter_source_files():
    """Itera los archivos .py de src/pymedia excluyendo el paquete locales/."""
    for path in SRC_DIR.rglob("*.py"):
        if LOCALES_DIR in path.parents:
            continue
        yield path


class TestBaseLocale:
    def test_base_locale_has_expected_dicts(self):
        """El locale base debe tener todos los dicts esperados."""
        en = _load_locale(BASE_LOCALE)
        for dict_name in EXPECTED_DICTS:
            assert hasattr(en, dict_name), f"en missing dict {dict_name}"

    def test_base_locale_no_empty_keys_or_values(self):
        """El locale base no debe tener llaves vacías ni valores vacíos o nulos."""
        en = _load_locale(BASE_LOCALE)
        _validate_locale_structure(en, BASE_LOCALE)


class TestLocalesConsistency:
    def test_same_dicts(self):
        """Cada locale debe tener exactamente los mismos dicts que en."""
        en = _load_locale(BASE_LOCALE)
        en_dicts = {name for name in dir(en) if not name.startswith("_") and isinstance(getattr(en, name), dict)}

        for lang in OTHER_LOCALES:
            locale = _load_locale(lang)
            locale_dicts = {name for name in dir(locale) if not name.startswith("_") and isinstance(getattr(locale, name), dict)}
            assert locale_dicts == en_dicts, \
                f"{lang}: dicts mismatch. Expected {sorted(en_dicts)}, got {sorted(locale_dicts)}"

    def test_same_keys(self):
        """Para cada dict, las llaves deben coincidir exactamente con las de en."""
        en = _load_locale(BASE_LOCALE)

        for lang in OTHER_LOCALES:
            locale = _load_locale(lang)
            for dict_name in EXPECTED_DICTS:
                en_keys = set(getattr(en, dict_name).keys())
                locale_keys = set(getattr(locale, dict_name).keys())
                assert locale_keys == en_keys, \
                    f"{lang}: {dict_name} keys mismatch. " \
                    f"Missing: {sorted(en_keys - locale_keys)}, " \
                    f"Extra: {sorted(locale_keys - en_keys)}"

    def test_same_params(self):
        """Para cada dict y llave, los parámetros deben coincidir con los de en."""
        en = _load_locale(BASE_LOCALE)

        for lang in OTHER_LOCALES:
            locale = _load_locale(lang)
            for dict_name in EXPECTED_DICTS:
                for key, en_message in getattr(en, dict_name).items():
                    locale_message = getattr(locale, dict_name)[key]
                    en_params = _extract_params(en_message)
                    locale_params = _extract_params(locale_message)
                    assert locale_params == en_params, \
                        f"{lang}: {dict_name}['{key}'] params mismatch. " \
                        f"Expected {sorted(en_params)}, got {sorted(locale_params)}"

    def test_no_empty_keys_or_values(self):
        """Los demás locales no deben tener llaves vacías ni valores vacíos o nulos."""
        for lang in OTHER_LOCALES:
            locale = _load_locale(lang)
            _validate_locale_structure(locale, lang)


class TestSourceCodeReferences:
    """Verifica que las referencias a locales en el código fuente existen en en."""

    def test_direct_locale_references_exist(self):
        """Toda referencia locales.DICT_NAME['MESSAGE_KEY'] debe existir en en."""
        en = _load_locale(BASE_LOCALE)
        pattern = re.compile(r"locales\.(\w+)\[\"(\w+)\"\]")

        for path in _iter_source_files():
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in pattern.finditer(line):
                    dict_name, key = match.group(1), match.group(2)
                    assert hasattr(en, dict_name), \
                        f"{path.name}:{line_no}: locales.{dict_name} does not exist in en"
                    assert key in getattr(en, dict_name), \
                        f"{path.name}:{line_no}: locales.{dict_name}['{key}'] does not exist in en"

    def test_logger_call_sites_exist(self):
        """Los keys de log_info/log_warning/log_debug deben existir en en."""
        en = _load_locale(BASE_LOCALE)
        logger_dicts = {
            "log_info": "Info",
            "log_warning": "Warnings",
            "log_debug": "Debug",
        }
        pattern = re.compile(r"log_(info|warning|debug)\(\s*\w+,\s*\"(\w+)\"")

        for path in _iter_source_files():
            for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                for match in pattern.finditer(line):
                    func, key = match.group(1), match.group(2)
                    dict_name = logger_dicts[f"log_{func}"]
                    assert key in getattr(en, dict_name), \
                        f"{path.name}:{line_no}: log_{func}('{key}') does not exist in en.{dict_name}"

    def test_error_message_keys_exist(self):
        """Los message_key de las subclases de PyMediaError deben existir en en."""
        import pymedia.errors as errors_module

        en = _load_locale(BASE_LOCALE)
        category_dicts = {
            "ValidationError": "ValidationError",
            "PipelineError": "PipelineError",
            "ExecutionError": "ExecutionError",
        }

        for _, cls in inspect.getmembers(errors_module, inspect.isclass):
            if not issubclass(cls, errors_module.PyMediaError):
                continue
            if cls is errors_module.PyMediaError:
                continue
            message_key = getattr(cls, "message_key", "")
            category = getattr(cls, "category", "")
            if not message_key or not category:
                continue
            dict_name = category_dicts.get(category)
            assert dict_name is not None, f"{cls.__name__}: unknown category '{category}'"
            assert message_key in getattr(en, dict_name), \
                f"{cls.__name__}: message_key '{message_key}' does not exist in en.{dict_name}"
