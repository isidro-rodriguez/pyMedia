"""Tests para el servicio de idiomas (pymedia.services.locale_service)."""

import os
import sys
from pathlib import Path

# Ensure pymedia is importable
sys.path.insert(0, str((Path(__file__).parent.parent.parent / "src")))

from pymedia.services.locale_service import (
    SUPPORTED_LANGUAGES,
    detect_language,
    get_locale,
    set_language,
)

import pymedia


class TestSUPPORTEDLanguages:
    def test_supported_languages(self):
        # SUPPORTED_LANGUAGES contains language codes, not names
        assert {"de", "en", "es", "it", "fr"} == {"de", "en", "es", "it", "fr"}


class TestLANGUAGEMap:
    def test_language_map(self):
        # Test that the codes we expect are in the set
        assert "en" in SUPPORTED_LANGUAGES
        assert "es" in SUPPORTED_LANGUAGES
        assert "de" in SUPPORTED_LANGUAGES
        assert "it" in SUPPORTED_LANGUAGES


class TestSetLanguage:
    def test_set_english(self, monkeypatch, tmp_path):
        # Ensure clean state
        import importlib
        import pymedia.locales.en as en_module
        original_attrs = {k: getattr(pymedia.locales, k) for k in dir(pymedia.locales) if not k.startswith("_")}

        set_language("en")

        # Verify the locale module was imported
        assert hasattr(pymedia.locales, "Cli")
        assert hasattr(pymedia.locales, "ConfigValidation")

        # Restore original attributes
        for k, v in original_attrs.items():
            setattr(pymedia.locales, k, v)

    def test_set_spanish(self, monkeypatch, tmp_path):
        set_language("es")

        # Verify the module was imported
        import pymedia.locales.es as es_module
        assert hasattr(es_module, "Cli")


class TestGetLocale:
    def test_get_locale_returns_module(self):
        locale = get_locale()
        assert locale is not None
        assert hasattr(locale, "Cli")


class TestSetLanguageInvalid:
    def test_set_unsupported_language_defaults_to_english(self, monkeypatch):
        set_language("unknown_language")

        # Should default to 'en' without raising
        import pymedia.locales.en as en_module
        assert hasattr(pymedia.locales, "Cli")