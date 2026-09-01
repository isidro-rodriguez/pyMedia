"""Tests de la clase `_LocaleManager` del sistema gettext de pyMedia.

Valora detección de idioma, carga de catálogos, traducción y plurales.
"""

import os
from pathlib import Path
from unittest.mock import patch

from pymedia.locale_manager import _LocaleManager, locale_manager

_SRC_DIR = Path(__file__).resolve().parents[1] / "src"
_LOCALEDIR = _SRC_DIR / "pymedia" / "locales"


# ─── 1) Singleton e instanciación ─────────────────────────────────────────


def test_singleton_existe() -> None:
    """El singleton `locale_manager` es una instancia de `_LocaleManager`."""
    assert isinstance(locale_manager, _LocaleManager)


def test_instancia_custom_localedir(tmp_path: Path) -> None:
    """Puede instanciarse con un localedir arbitrario."""
    mgr = _LocaleManager(localedir=tmp_path)
    assert mgr.localedir == tmp_path


def test_localedir_por_defecto() -> None:
    """El localedir por defecto apunta a `src/pymedia/locales`."""
    mgr = _LocaleManager()
    assert mgr.localedir == _LOCALEDIR


# ─── 2) Detección de idioma ───────────────────────────────────────────────


def test_detect_language_devuelve_codigo_valido() -> None:
    """`detect_language` devuelve un código en `SUPPORTED_LANGUAGES`."""
    mgr = _LocaleManager()
    codigo = mgr.detect_language()
    assert codigo in mgr.SUPPORTED_LANGUAGES


def test_detect_language_usa_config_toml(tmp_path: Path) -> None:
    """Si config.toml define un idioma válido, se respeta."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text(
        '[app]\nlanguage = "spanish"\n', encoding="utf-8"
    )
    mgr = _LocaleManager()
    with patch.dict(
        os.environ,
        {"XDG_CONFIG_HOME": str(tmp_path)},
        clear=False,
    ):
        with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
            assert mgr.detect_language() == "es"


def test_detect_language_fallback_en() -> None:
    """Sin configuración ni variables de entorno, el resultado es válido."""
    mgr = _LocaleManager()
    env_limpio = {k: v for k, v in os.environ.items() if k not in ("LANG", "LC_ALL")}
    with patch.dict(os.environ, env_limpio, clear=True):
        resultado = mgr.detect_language()
        assert resultado in mgr.SUPPORTED_LANGUAGES


# ─── 3) Carga de catálogos ────────────────────────────────────────────────


def test_set_language_carga_sin_error() -> None:
    """`set_language` carga catálogos soportados sin lanzar excepciones."""
    mgr = _LocaleManager()
    for lang in mgr.SUPPORTED_LANGUAGES:
        mgr.set_language(lang)
        assert mgr.get_translation() is not None


def test_set_language_fallback_no_soportado() -> None:
    """Un idioma no soportado recae en `en` (NullTranslations)."""
    mgr = _LocaleManager()
    mgr.set_language("fr")  # no soportado
    traduccion = mgr.get_translation()
    # NullTranslations.gettext devuelve el msgid sin cambios
    assert traduccion.gettext("Hello") == "Hello"


# ─── 4) Traducción ────────────────────────────────────────────────────────


def test_traduje_idioma_sin_catalogo() -> None:
    """Con `en` (sin catálogo) el msgid se devuelve intacto."""
    mgr = _LocaleManager()
    mgr.set_language("en")
    assert mgr.translate("Hello, world!") == "Hello, world!"


def test_traduje_con_catalgo_es() -> None:
    """Con `es` cargado, un msgid conocido se traduce."""
    mgr = _LocaleManager()
    mgr.set_language("es")
    traduccion = mgr.translate("Channels")
    assert traduccion == "Canales"


def test_traduccion_con_placeholder() -> None:
    """La interpolación con `%(name)s` funciona tras traducir."""
    mgr = _LocaleManager()
    mgr.set_language("es")
    traduccion = mgr.translate("Could not create directory: %(path)s")
    resultado = traduccion % {"path": "/tmp/foo"}
    assert "/tmp/foo" in resultado


# ─── 5) Plurales ──────────────────────────────────────────────────────────


def test_ngettext_singular() -> None:
    """`ngettext` devuelve el singular cuando n == 1."""
    mgr = _LocaleManager()
    mgr.set_language("en")
    resultado = mgr.ngettext("one file", "many files", 1)
    assert resultado == "one file"


def test_ngettext_plural() -> None:
    """`ngettext` devuelve el plural cuando n != 1."""
    mgr = _LocaleManager()
    mgr.set_language("en")
    resultado = mgr.ngettext("one file", "many files", 5)
    assert resultado == "many files"
