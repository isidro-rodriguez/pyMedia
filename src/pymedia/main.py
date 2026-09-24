"""Punto de entrada de la CLI de pyMedia.

Construye la aplicación Typer, registra los subcomandos y configura la codificación
de la salida estándar en Windows.
"""

import io
import sys
from typing import Any, cast

import typer

from pymedia.locale_manager import locale_manager


def _configure_runtime() -> None:
    """Configura idioma y codificación antes de importar los subcomandos.

    El idioma debe fijarse antes de importar los módulos de comandos, ya que
    estos usan `_()` en sus `help=` al definirse. En Windows, stdout se
    reconfigura a UTF-8 para evitar errores de codificación en la salida.
    """
    locale_manager.set_language(locale_manager.detect_language())

    if sys.platform == "win32" and type(sys.stdout) is io.TextIOWrapper:
        cast("io.TextIOWrapper[Any]", sys.stdout).reconfigure(encoding="utf-8")


def _build_app() -> typer.Typer:
    """Importa los subcomandos y los registra en la aplicación principal.

    Los imports se difieren a esta función (en vez de ir a nivel de módulo)
    para garantizar que `_configure_runtime` se ejecuta antes de que cualquier
    módulo de comandos se cargue.

    Returns:
        Aplicación Typer con todos los subcomandos registrados.
    """
    from pymedia.commands.add_audio.cli import add_audio_cli
    from pymedia.commands.add_subtitles.cli import add_subs_cli
    from pymedia.commands.animated.cli import animated_cli
    from pymedia.commands.cut.cli import cut_cli
    from pymedia.commands.delete_audio.cli import delete_audio_cli
    from pymedia.commands.delete_subtitles.cli import delete_subs_cli
    from pymedia.commands.edit_audio.cli import edit_audio_cli
    from pymedia.commands.edit_subtitles.cli import edit_subs_cli
    from pymedia.commands.extract_audio.cli import extract_audio_cli
    from pymedia.commands.extract_subtitles.cli import extract_subs_cli
    from pymedia.commands.frames.cli import frames_cli
    from pymedia.commands.info.cli import info_cli
    from pymedia.commands.interval.cli import interval_cli
    from pymedia.commands.join.cli import join_cli
    from pymedia.commands.main.cli import main_cli
    from pymedia.commands.remux.cli import remux_cli
    from pymedia.commands.scene.cli import scene_cli
    from pymedia.commands.sheet.cli import sheet_cli
    from pymedia.commands.transcode.cli import transcode_cli

    built_app = main_cli
    built_app.add_typer(info_cli)
    built_app.add_typer(sheet_cli)
    built_app.add_typer(transcode_cli)
    built_app.add_typer(remux_cli)
    built_app.add_typer(cut_cli)
    built_app.add_typer(join_cli)
    built_app.add_typer(add_audio_cli)
    built_app.add_typer(delete_audio_cli)
    built_app.add_typer(edit_audio_cli)
    built_app.add_typer(extract_audio_cli)
    built_app.add_typer(add_subs_cli)
    built_app.add_typer(delete_subs_cli)
    built_app.add_typer(edit_subs_cli)
    built_app.add_typer(extract_subs_cli)
    built_app.add_typer(animated_cli)
    built_app.add_typer(frames_cli)
    built_app.add_typer(interval_cli)
    built_app.add_typer(scene_cli)
    return built_app


_configure_runtime()
app = _build_app()


if __name__ == "__main__":
    app()
