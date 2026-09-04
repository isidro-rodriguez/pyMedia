# ruff: noqa: E402
"""Punto de entrada de la CLI de pyMedia.

Construye la aplicación Typer, registra los subcomandos y configura la codificación
de la salida estándar en Windows.
"""

import io
import sys

from pymedia.locale_manager import locale_manager

# Cargar el idioma ANTES de importar typer_options (que usa locales en los help=)
locale_manager.set_language(locale_manager.detect_language())

from pymedia.typer.commands.gif_command import gif_command
from pymedia.typer.commands.info_command import info_command
from pymedia.typer.commands.sheet_command import sheet_command
from pymedia.typer.commands.thumb_commands import (
    frames_command,
    interval_command,
    scene_command,
)
from pymedia.typer.instance import typer_instance

if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

app = typer_instance
app.add_typer(typer_instance=info_command, rich_help_panel="Analysis commands")

app.add_typer(typer_instance=frames_command, rich_help_panel="Image commands")
app.add_typer(typer_instance=gif_command, rich_help_panel="Image commands")
app.add_typer(typer_instance=interval_command, rich_help_panel="Image commands")
app.add_typer(typer_instance=scene_command, rich_help_panel="Image commands")
app.add_typer(typer_instance=sheet_command, rich_help_panel="Image commands")


if __name__ == "__main__":
    app()
