"""Servicio de detección y carga de idiomas (estándar gettext).

Los msgid se escriben en inglés en el código fuente y se traducen con
catálogos `.mo` alojados en `localedir/{lang}/LC_MESSAGES/`, donde `{lang}`
es el nombre completo en inglés (`spanish`, ...). El idioma base (`english`)
usa los msgid tal cual.
"""

import gettext
import locale
import os
import tomllib
from pathlib import Path

import platformdirs

from pymedia.data.language_codes import resolve_language


class _LocaleManager:
    """Gestión del idioma activo y del catálogo gettext.

    La detección sigue la prioridad: `PYMEDIA_LANG` > `config.toml` >
    sistema > `english`. Todas las vías aceptan código ISO 639-1, código
    ISO 639-2, nombre nativo o nombre en inglés.

    Attributes:
        DOMAIN: Nombre del dominio gettext (ficheros `pymedia.mo`).
        localedir: Directorio con los catálogos `{lang}/LC_MESSAGES/`.
        SUPPORTED_LANGUAGES: Nombres de idioma con catálogo disponible.
    """

    DOMAIN = "pymedia"
    SUPPORTED_LANGUAGES = frozenset({"english", "spanish"})
    """Nombres de idioma con catálogo gettext disponible."""

    def __init__(self, localedir: Path | None = None) -> None:
        """Inicializa el servicio con el catálogo `english` (no traduce nada).

        Args:
            localedir: Directorio raíz de catálogos. Si es `None`, se usa
                `_default_localedir()`.
        """
        self.localedir = Path(localedir) if localedir else self._default_localedir()
        self._translation = gettext.NullTranslations()
        self.set_language("english")

    @staticmethod
    def _default_localedir() -> Path:
        """Devuelve el directorio raíz de catálogos, sobreescribible vía env."""
        override = os.environ.get("PYMEDIA_LOCALEDIR")
        if override:
            return Path(override)
        return Path(__file__).resolve().parents[0] / "locales"

    @classmethod
    def _normalize(cls, raw: str) -> str | None:
        """Normaliza una especificación de idioma al nombre en inglés.

        Args:
            raw: Código ISO 639-1, código ISO 639-2, nombre nativo o nombre
                en inglés.

        Returns:
            El nombre en inglés si está soportado, o `None` en caso contrario.
        """
        lang = resolve_language(raw)
        if lang is None:
            return None
        name = lang.english.casefold()
        return name if name in cls.SUPPORTED_LANGUAGES else None

    def detect_language(self) -> str:
        """Detecta el idioma de la aplicación.

        Prioridad: `PYMEDIA_LANG` > `config.toml` > sistema > `english`.

        Returns:
            Nombre en inglés del idioma detectado.
        """

        def _read_env_language() -> str | None:
            """Lee `PYMEDIA_LANG` y lo normaliza, o `None` si no es válido."""
            value = os.environ.get("PYMEDIA_LANG", "")
            if not value.strip():
                return None
            return self._normalize(value)

        def _read_config_language() -> str:
            """Lee [app].language del config.toml sin validar."""
            path = (
                Path(
                    platformdirs.user_config_dir(
                        appname="pymedia", appauthor=False, roaming=True
                    )
                )
                / "config.toml"
            )
            if not path.exists():
                return "system"
            with path.open("rb") as f:
                data = tomllib.load(f)
            return str(data.get("app", {}).get("language", "system"))

        def _detect_system_language() -> str:
            """Detecta el idioma del sistema (POSIX, locale, fallback)."""
            # Precedencia POSIX: LANGUAGE > LC_ALL > LC_MESSAGES > LANG.
            lang = next(
                (
                    value
                    for name in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG")
                    if (value := os.environ.get(name, "").split(":")[0])
                ),
                "",
            )

            if not lang:
                try:
                    locale.setlocale(category=locale.LC_ALL, locale="")
                    lang = locale.getlocale()[0] or ""
                except (locale.Error, ValueError, TypeError):
                    lang = ""

            lang_code = lang.split("_")[0]
            normalized = self._normalize(lang_code) if lang_code else None
            return normalized if normalized is not None else "english"

        env_lang = _read_env_language()
        if env_lang is not None:
            return env_lang

        config_lang = _read_config_language()
        if config_lang.strip().casefold() != "system":
            code = self._normalize(config_lang)
            if code is not None:
                return code
        return _detect_system_language()

    def set_language(self, lang: str) -> None:
        """Carga el catálogo gettext del idioma indicado.

        Los catálogos viven en `{localedir}/{nombre}/LC_MESSAGES/`, con el
        nombre completo en inglés. Se cargan por ruta directa porque la
        normalización interna de `gettext` solo entiende códigos de locale
        (`es`, `es_ES`, ...) y nunca el literal `spanish`.

        Args:
            lang: Código ISO 639-1, código ISO 639-2, nombre nativo o nombre
                en inglés. Si no está soportado, se usa `english`.
        """
        normalized = self._normalize(lang)
        if normalized is None:
            normalized = "english"
        mo_path = self.localedir / normalized / "LC_MESSAGES" / f"{self.DOMAIN}.mo"
        try:
            with mo_path.open("rb") as f:
                self._translation = gettext.GNUTranslations(f)
        except OSError:
            self._translation = gettext.NullTranslations()

    def get_translation(self) -> gettext.NullTranslations:
        """Devuelve el objeto de traducción activo.

        Returns:
            El traductor `gettext` cargado por `set_language`.
        """
        return self._translation

    def translate(self, message: str) -> str:
        """Traduce `msg` al idioma activo.

        Args:
            message: msgid en inglés a traducir.

        Returns:
            El mensaje traducido, o `msg` sin cambios si no hay
            entrada en el catálogo activo.
        """
        return self._translation.gettext(message)

    def ngettext(self, singular: str, plural: str, n: int) -> str:
        """Traduce eligiendo singular o plural según `n`.

        Args:
            singular: msgid en inglés para `n == 1`.
            plural: msgid en inglés para el resto de casos.
            n: Cantidad que determina la forma a usar.

        Returns:
            El mensaje traducido en la forma correspondiente a `n`.
        """
        return self._translation.ngettext(msgid1=singular, msgid2=plural, n=n)


locale_manager = _LocaleManager()
