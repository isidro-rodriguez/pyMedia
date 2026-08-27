"""Servicio de detección y carga de idiomas."""

import importlib
import locale
import os
import tomllib
from pathlib import Path

import platformdirs

from pymedia import locales as package

LANGUAGE_MAP = {
    "system": None,
    "english": "en",
    "spanish": "es",
}

SUPPORTED_LANGUAGES = {"en", "es"}

_current_locale = None


def detect_language() -> str:
    """
    Detecta el lenguaje que va a utilizar la aplicación.
    Prioridad: config.toml > sistema > 'en'.

    Returns:
        Código i18n del locale a utilizar.
    """

    def _read_config_language() -> str:
        """Lee [app].language del config.toml sin validar."""
        path = (
            Path(platformdirs.user_config_dir("pymedia", appauthor=False, roaming=True))
            / "config.toml"
        )
        if not path.exists():
            return "system"
        with path.open("rb") as f:
            data = tomllib.load(f)
        return data.get("app", {}).get("language", "system")

    def _detect_system_language() -> str:
        """Detecta el idioma del sistema (env vars POSIX, locale, fallback 'en')."""
        lang = os.environ.get("LANG") or os.environ.get("LC_ALL") or ""

        if not lang:
            try:
                locale.setlocale(category=locale.LC_ALL, locale="")
                lang = locale.getlocale()[0] or ""
            except (locale.Error, ValueError, TypeError):
                lang = ""

        lang_code = lang.split("_")[0].lower()
        return lang_code if lang_code in SUPPORTED_LANGUAGES else "en"

    config_lang = _read_config_language()
    code = LANGUAGE_MAP.get(config_lang)

    if code is not None:
        return code

    return _detect_system_language()


def get_locale():
    """
    Devuelve el módulo de idioma activo.

    Si no hay ningún idioma cargado todavía, detecta el idioma del
    sistema y lo carga antes de devolverlo.

    Returns:
        El módulo del idioma actualmente activo.
    """

    if _current_locale is None:
        set_language(detect_language())
    return _current_locale


def set_language(lang: str) -> None:
    """Carga el módulo de idioma y expone sus dicts en `pymedia.locales`."""

    def _update_package_attributes() -> None:
        """Expone los dicts del idioma activo como atributos de `pymedia.locales`."""
        for name in (
            "Cli",
            "ConfigValidation",
            "Debug",
            "ExecutionError",
            "Info",
            "ParameterError",
            "Progress",
            "ValidationError",
            "Warnings",
        ):
            setattr(package, name, getattr(_current_locale, name))

    global _current_locale
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    _current_locale = importlib.import_module(f"pymedia.locales.{lang}")
    _update_package_attributes()
