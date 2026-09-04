"""Punto de entrada de la CLI de pyMedia.

Construye la aplicación Typer, registra los subcomandos y configura la codificación
de la salida estándar en Windows.
"""

import io
import sys

from pymedia.locale_manager import locale_manager
from pymedia.typer.commands import gif_command, info_command, sheet_command

# Cargar el idioma ANTES de importar typer_options (que usa locales en los help=)
locale_manager.set_language(locale_manager.detect_language())

from pymedia.typer.instance import typer_instance  # noqa: E402

if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

app = typer_instance()
app.add_typer(typer_instance=gif_command)
app.add_typer(typer_instance=info_command)
app.add_typer(typer_instance=sheet_command)


if __name__ == "__main__":
    app()
