"""Servicio de detección y carga de idiomas."""

import importlib
import os
import tomllib
from pathlib import Path

import platformdirs

LANGUAGE_MAP = {
    "system": None,
    "english": "en",
    "spanish": "es",
    "italian": "it",
    "french": "fr",
}
SUPPORTED_LANGUAGES = {"en", "es", "it", "fr"}
_current_locale = None


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
    """Detecta el idioma del sistema (LANG, LC_ALL, fallback 'en')."""
    lang = os.environ.get("LANG") or os.environ.get("LC_ALL") or ""
    code = lang.split("_")[0].lower()
    return code if code in SUPPORTED_LANGUAGES else "en"


def detect_language() -> str:
    """Prioridad: config.toml > sistema > 'en'."""
    config_lang = _read_config_language()
    code = LANGUAGE_MAP.get(config_lang)
    if code is not None:
        return code
    return _detect_system_language()


def set_language(lang: str) -> None:
    """Carga el módulo de idioma y expone sus dicts en `pymedia.locales`."""
    global _current_locale
    if lang not in SUPPORTED_LANGUAGES:
        lang = "en"
    _current_locale = importlib.import_module(f"pymedia.locales.{lang}")
    _update_package_attributes()


def _update_package_attributes() -> None:
    """Expone los dicts del idioma activo como atributos de `pymedia.locales`."""
    import pymedia.locales as package

    for name in (
        "Cli",
        "ConfigValidation",
        "Debug",
        "ExecutionError",
        "Info",
        "PipelineError",
        "Progress",
        "ValidationError",
        "Warnings",
    ):
        setattr(package, name, getattr(_current_locale, name))


def get_locale():
    """Devuelve el módulo de idioma activo."""
    if _current_locale is None:
        set_language(detect_language())
    return _current_locale
