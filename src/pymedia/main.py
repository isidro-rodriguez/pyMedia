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

if sys.platform == "win32" and isinstance(sys.stdout, io.TextIOWrapper):
    sys.stdout.reconfigure(encoding="utf-8")

from pymedia.typer.commands.audio_commands import audio_typer
from pymedia.typer.commands.gif_command import gif_typer
from pymedia.typer.commands.info_command import info_typer
from pymedia.typer.commands.sheet_command import sheet_typer
from pymedia.typer.commands.subtitles_commands import subtitles_typer
from pymedia.typer.commands.thumb_commands import thumb_typer
from pymedia.typer.commands.transcode_command import transcode_typer
from pymedia.typer.instance import typer_instance

app = typer_instance
app.add_typer(info_typer)
app.add_typer(sheet_typer)
app.add_typer(transcode_typer)
app.add_typer(audio_typer)
app.add_typer(subtitles_typer)
app.add_typer(gif_typer)
app.add_typer(thumb_typer)


if __name__ == "__main__":
    app()
