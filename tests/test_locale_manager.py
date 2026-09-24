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


def test_detect_language_devuelve_nombre_valido() -> None:
    """`detect_language` devuelve un nombre en `SUPPORTED_LANGUAGES`."""
    mgr = _LocaleManager()
    nombre = mgr.detect_language()
    assert nombre in mgr.SUPPORTED_LANGUAGES


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
            assert mgr.detect_language() == "spanish"


def test_detect_language_usa_env_var(tmp_path: Path) -> None:
    """`PYMEDIA_LANG` (ISO 639-2) tiene prioridad sobre config.toml y sistema."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text(
        '[app]\nlanguage = "spanish"\n', encoding="utf-8"
    )
    mgr = _LocaleManager()
    with patch.dict(os.environ, {"PYMEDIA_LANG": "eng"}, clear=False):
        with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
            assert mgr.detect_language() == "english"


def test_detect_language_env_var_acepta_nombre_de_idioma() -> None:
    """`PYMEDIA_LANG` acepta los nombres admitidos en `config.toml`."""
    mgr = _LocaleManager()
    with patch.dict(os.environ, {"PYMEDIA_LANG": "spanish"}, clear=False):
        assert mgr.detect_language() == "spanish"


def test_detect_language_env_var_normaliza_el_valor() -> None:
    """Mayúsculas y espacios en `PYMEDIA_LANG` no impiden el override."""
    mgr = _LocaleManager()
    with patch.dict(os.environ, {"PYMEDIA_LANG": " SPA "}, clear=False):
        assert mgr.detect_language() == "spanish"


def test_detect_language_env_var_ignora_valor_no_soportado(tmp_path: Path) -> None:
    """Un `PYMEDIA_LANG` desconocido no altera la detección normal."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text(
        '[app]\nlanguage = "english"\n', encoding="utf-8"
    )
    mgr = _LocaleManager()
    with patch.dict(os.environ, {"PYMEDIA_LANG": "fr"}, clear=False):
        with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
            assert mgr.detect_language() == "english"


def test_detect_language_env_var_acepta_iso_639_1(tmp_path: Path) -> None:
    """El override acepta ISO 639-1 (`en`/`es`), como `--language`."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    (config_dir / "config.toml").write_text(
        '[app]\nlanguage = "english"\n', encoding="utf-8"
    )
    mgr = _LocaleManager()
    with patch.dict(os.environ, {"PYMEDIA_LANG": "es"}, clear=False):
        with patch("platformdirs.user_config_dir", return_value=str(config_dir)):
            assert mgr.detect_language() == "spanish"


def test_detect_language_env_var_acepta_nombre_nativo() -> None:
    """El override acepta el nombre nativo (`Español`)."""
    mgr = _LocaleManager()
    with patch.dict(os.environ, {"PYMEDIA_LANG": "Español"}, clear=False):
        assert mgr.detect_language() == "spanish"


def test_detect_language_fallback_english() -> None:
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
    """Un idioma no soportado recae en `english` (NullTranslations)."""
    mgr = _LocaleManager()
    mgr.set_language("french")  # existe pero sin catálogo soportado
    traduccion = mgr.get_translation()
    # NullTranslations.gettext devuelve el msgid sin cambios
    assert traduccion.gettext("Hello") == "Hello"


def test_set_language_acepta_alias() -> None:
    """`set_language` acepta códigos ISO y nombres nativos."""
    mgr = _LocaleManager()
    for alias in ("es", "spa", "Español", "spanish", "SPANISH"):
        mgr.set_language(alias)
        assert mgr.translate("Channels") == "Canales"


# ─── 4) Traducción ────────────────────────────────────────────────────────


def test_traduje_idioma_sin_catalogo() -> None:
    """Con `english` (sin catálogo) el msgid se devuelve intacto."""
    mgr = _LocaleManager()
    mgr.set_language("english")
    assert mgr.translate("Hello, world!") == "Hello, world!"


def test_traduje_con_catalogo_spanish() -> None:
    """Con `spanish` cargado, un msgid conocido se traduce."""
    mgr = _LocaleManager()
    mgr.set_language("spanish")
    traduccion = mgr.translate("Channels")
    assert traduccion == "Canales"


def test_traduccion_con_placeholder() -> None:
    """La interpolación con `%(name)s` funciona tras traducir."""
    mgr = _LocaleManager()
    mgr.set_language("spanish")
    traduccion = mgr.translate("Could not create directory: %(path)s")
    resultado = traduccion % {"path": "/tmp/foo"}
    assert "/tmp/foo" in resultado


# ─── 5) Plurales ──────────────────────────────────────────────────────────


def test_ngettext_singular() -> None:
    """`ngettext` devuelve el singular cuando n == 1."""
    mgr = _LocaleManager()
    mgr.set_language("english")
    resultado = mgr.ngettext("one file", "many files", 1)
    assert resultado == "one file"


def test_ngettext_plural() -> None:
    """`ngettext` devuelve el plural cuando n != 1."""
    mgr = _LocaleManager()
    mgr.set_language("english")
    resultado = mgr.ngettext("one file", "many files", 5)
    assert resultado == "many files"
