"""Servicio de detección y carga de idiomas (estándar gettext).

Los msgid se escriben en inglés en el código fuente y se traducen con
catálogos `.mo` alojados en `localedir/{lang}/LC_MESSAGES/`. Los idiomas sin
catálogo (caso de `en`) usan los msgid tal cual.
"""

import gettext
import locale
import os
import tomllib
from pathlib import Path

import platformdirs


class _LocaleManager:
    """Gestión del idioma activo y del catálogo gettext.

    La detección sigue la prioridad: `config.toml` > sistema > `en`.

    Attributes:
        DOMAIN: Nombre del dominio gettext (ficheros `pymedia.mo`).
        localedir: Directorio con los catálogos `{lang}/LC_MESSAGES/`.
    """

    DOMAIN = "pymedia"
    LANGUAGE_MAP = {
        "system": None,
        "english": "en",
        "spanish": "es",
    }
    SUPPORTED_LANGUAGES = {"en", "es"}

    def __init__(self, localedir: Path | None = None) -> None:
        """Inicializa el servicio con el catálogo `en` (no traduce nada).

        Args:
            localedir: Directorio raíz de catálogos. Si es `None`, se usa
                `_default_localedir()`.
        """
        self.localedir = Path(localedir) if localedir else self._default_localedir()
        self._translation = gettext.NullTranslations()
        self.set_language("en")

    @staticmethod
    def _default_localedir() -> Path:
        # Directorio raíz de catálogos, sobreescribible para builds frozen.
        override = os.environ.get("PYMEDIA_LOCALEDIR")
        if override:
            return Path(override)
        return Path(__file__).resolve().parents[0] / "locales"

    def detect_language(self) -> str:
        """Detecta el idioma de la aplicación.

        Prioridad: `config.toml` > sistema > `en`.

        Returns:
            Código i18n del idioma detectado.
        """

        def _read_config_language() -> str:
            # Lee [typer_instance].language del config.toml sin validar.
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
            return data.get("typer_instance", {}).get("language", "system")

        def _detect_system_language() -> str:
            # Detecta el idioma del sistema (env vars POSIX, locale, fallback 'en').
            lang = os.environ.get("LANG") or os.environ.get("LC_ALL") or ""

            if not lang:
                try:
                    locale.setlocale(category=locale.LC_ALL, locale="")
                    lang = locale.getlocale()[0] or ""
                except (locale.Error, ValueError, TypeError):
                    lang = ""

            lang_code = lang.split("_")[0].lower()
            return lang_code if lang_code in self.SUPPORTED_LANGUAGES else "en"

        config_lang = _read_config_language()
        code = self.LANGUAGE_MAP.get(config_lang)
        if code is not None:
            return code
        return _detect_system_language()

    def set_language(self, lang: str) -> None:
        """Carga el catálogo gettext del idioma indicado.

        Args:
            lang: Código i18n a cargar. Si no está soportado, se usa `en`.
        """
        if lang not in self.SUPPORTED_LANGUAGES:
            lang = "en"
        self._translation = gettext.translation(
            domain=self.DOMAIN,
            localedir=self.localedir,
            languages=[lang],
            fallback=True,
        )

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
