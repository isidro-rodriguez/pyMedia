"""Punto de entrada de la CLI de pyMedia.

Construye la aplicación Typer, registra los subcomandos y configura la codificación
de la salida estándar en Windows.
"""

import io
import sys

from pymedia.locale_manager import locale_manager
from pymedia.typer.commands.gif_command import gif
from pymedia.typer.commands.info_command import info
from pymedia.typer.commands.screenshoot_command import screenshoot
from pymedia.typer.commands.sheet_command import sheet

# Cargar el idioma ANTES de importar typer_options (que usa locales en los help=)
locale_manager.set_language(locale_manager.detect_language())

from pymedia.typer.instance import typer_instance  # noqa: E402

if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

app = typer_instance
app.add_typer(typer_instance=gif, name="gif")
app.add_typer(typer_instance=info, name="info")
app.add_typer(typer_instance=screenshoot, name="screenshoot")
app.add_typer(typer_instance=sheet, name="sheet")


if __name__ == "__main__":
    app()
