"""Paquete de idiomas de pyMedia (estándar gettext).

Los mensajes se escriben en inglés en el código fuente (msgid) y se traducen
mediante los catálogos `.po`/`.mo` alojados en
`pymedia/locales/<lang>/LC_MESSAGES/pymedia.mo`. Los idiomas sin catálogo
(caso de `en`) usan los msgid tal cual.

Uso típico:

    from pymedia.locales import translate as _

    print(_("Hello, world!"))
"""

from pymedia.locale_manager import locale_manager

translate = locale_manager.translate
ngettext = locale_manager.ngettext

locale_manager.set_language(locale_manager.detect_language())
