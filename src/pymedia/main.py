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

from pymedia.commands.add_audio.cli import add_audio_cli
from pymedia.commands.add_subs.cli import add_subs_cli
from pymedia.commands.animated.cli import animated_cli
from pymedia.commands.cut.cli import cut_cli
from pymedia.commands.delete_audio.cli import delete_audio_cli
from pymedia.commands.delete_subs.cli import delete_subs_cli
from pymedia.commands.edit_audio.cli import edit_audio_cli
from pymedia.commands.edit_subs.cli import edit_subs_cli
from pymedia.commands.extract_audio.cli import extract_audio_cli
from pymedia.commands.extract_subs.cli import extract_subs_cli
from pymedia.commands.frames.cli import frames_cli
from pymedia.commands.info.cli import info_cli
from pymedia.commands.interval.cli import interval_cli
from pymedia.commands.join.cli import join_cli
from pymedia.commands.remux.cli import remux_cli
from pymedia.commands.scene.cli import scene_cli
from pymedia.commands.sheet.cli import sheet_cli
from pymedia.commands.transcode.cli import transcode_cli
from pymedia.typer.instance import typer_instance

app = typer_instance
app.add_typer(info_cli)
app.add_typer(sheet_cli)
app.add_typer(transcode_cli)
app.add_typer(remux_cli)
app.add_typer(cut_cli)
app.add_typer(join_cli)
app.add_typer(add_audio_cli)
app.add_typer(delete_audio_cli)
app.add_typer(edit_audio_cli)
app.add_typer(extract_audio_cli)
app.add_typer(add_subs_cli)
app.add_typer(delete_subs_cli)
app.add_typer(edit_subs_cli)
app.add_typer(extract_subs_cli)
app.add_typer(animated_cli)
app.add_typer(frames_cli)
app.add_typer(interval_cli)
app.add_typer(scene_cli)


if __name__ == "__main__":
    app()
