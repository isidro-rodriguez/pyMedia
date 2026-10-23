"""Tests de la capa visual: tema, consola, preguntas, logs y ayuda."""

import logging
from io import StringIO

import pytest
import typer
from rich.console import Console
from rich.text import Text
from typer import rich_utils

from pymedia import ui
from pymedia.commands.base.service import format_cmd
from pymedia.logger import Logger, _ConsoleHandler, _render_markup
from pymedia.theme import THEME


def _record_console() -> Console:
    """Consola temática que escribe en memoria, sin colores."""
    return Console(theme=THEME, file=StringIO(), width=100, color_system=None)


# =============================================================================
#  Tema
# =============================================================================


@pytest.mark.parametrize(
    "name",
    ["primary", "success", "warning", "error", "heading", "border", "prompt"],
)
def test_theme_defines_the_proposed_semantic_styles(name: str) -> None:
    """El tema contiene los estilos semánticos de la propuesta."""
    assert name in THEME.styles


# =============================================================================
#  Preguntas
# =============================================================================


@pytest.mark.parametrize(
    ("answer", "expected"),
    [
        ("y", True),
        ("YES", True),
        ("s", True),
        ("sí", True),
        ("n", False),
        ("No", False),
    ],
)
def test_confirm_accepts_english_and_spanish_answers(
    monkeypatch: pytest.MonkeyPatch, answer: str, expected: bool
) -> None:
    """Se aceptan respuestas en inglés y español, sin distinguir mayúsculas."""
    monkeypatch.setattr(ui, "console", _record_console())
    monkeypatch.setattr("sys.stdin", StringIO(f"{answer}\n"))

    assert ui.confirm("Overwrite?") is expected


def test_confirm_uses_default_on_empty_answer(monkeypatch: pytest.MonkeyPatch) -> None:
    """Intro sin respuesta devuelve el valor por defecto."""
    monkeypatch.setattr(ui, "console", _record_console())
    monkeypatch.setattr("sys.stdin", StringIO("\n"))

    assert ui.confirm("Convert?", default=True) is True


def test_confirm_aborts_when_input_is_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    """Sin entrada (EOF) se aborta como hacía `typer.confirm`."""
    monkeypatch.setattr(ui, "console", _record_console())
    monkeypatch.setattr("sys.stdin", StringIO(""))

    with pytest.raises(typer.Abort):
        ui.confirm("Overwrite?")


# =============================================================================
#  Ayuda y Typer
# =============================================================================


def test_styled_help_marks_headings_and_examples() -> None:
    """Las cabeceras pasan a `heading` y los ejemplos a `code` escapado."""
    text = "Intro.\n\n[bold]Examples[/bold]:\n  > pymedia info [x].mp4\n"

    styled = ui.styled_help(text)

    assert "[heading]Examples[/heading]" in styled
    assert "[dim]$[/dim] [code]pymedia info \\[x].mp4[/code]" in styled


def test_install_typer_theme_styles_help_and_errors() -> None:
    """Typer usa los colores del tema y su consola resuelve estilos con nombre."""
    ui.install_typer_theme()

    assert rich_utils.STYLE_ERRORS_PANEL_BORDER == str(THEME.styles["error"])
    assert rich_utils.STYLE_OPTION == str(THEME.styles["help.option"])
    console = rich_utils._get_rich_console()
    assert console.get_style("heading") == THEME.styles["heading"]


# =============================================================================
#  Logs
# =============================================================================


def _emit(level: int, msg: str, **extra: object) -> str:
    """Renderiza un registro con el handler de consola y devuelve el texto."""
    console = _record_console()
    handler = _ConsoleHandler(console=console, debug=False)
    record = logging.LogRecord("pymedia", level, "", 0, msg, None, None)
    for key, value in extra.items():
        setattr(record, key, value)
    handler.emit(record)
    file = console.file
    assert isinstance(file, StringIO)
    return file.getvalue()


@pytest.mark.parametrize(
    ("level", "extra", "icon"),
    [
        (logging.INFO, {}, "ℹ"),
        (logging.INFO, {"success": True}, "✔"),
        (logging.WARNING, {}, "▲"),
        (logging.ERROR, {}, "✖"),
    ],
)
def test_console_handler_prefixes_an_icon_per_level(
    level: int, extra: dict[str, object], icon: str
) -> None:
    """Cada nivel se muestra con su icono delante del mensaje."""
    assert _emit(level, "Hecho", **extra).startswith(f"{icon} Hecho")


def test_console_handler_aligns_multiline_messages() -> None:
    """Las líneas siguientes se alinean con el texto, no con el icono."""
    output = _emit(logging.ERROR, "Primera\nSegunda")

    assert output.splitlines()[1] == "  Segunda"


def test_render_markup_escapes_brackets_and_highlights_values() -> None:
    """Los corchetes del texto se muestran tal cual y los valores se resaltan."""
    rendered = _render_markup("Ver [https://x.org] %(path)s", {"path": "a[1].mp4"})

    assert Text.from_markup(rendered).plain == "Ver [https://x.org] a[1].mp4"
    assert "[highlight]" in rendered


def test_logger_writes_plain_text_to_the_log_file(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """El fichero de log recibe el mensaje sin markup."""
    with caplog.at_level(logging.INFO, logger="pymedia"):
        Logger(logging.getLogger("pymedia.test")).success(
            "Saved: %(output)s", output="out.mp4"
        )

    assert caplog.records[-1].getMessage() == "Saved: out.mp4"
    assert getattr(caplog.records[-1], "success", False) is True


# =============================================================================
#  Comando ffmpeg (--show-cmd)
# =============================================================================


def test_format_cmd_colors_tokens_without_changing_the_text(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """El color no altera el comando, que sigue siendo copiable."""
    monkeypatch.setattr("os.name", "posix")

    text = format_cmd(["ffmpeg", "-i", "in put.mkv", "-c", "copy", "out.mp4"])

    assert text.plain == "\nffmpeg -i 'in put.mkv' -c copy out.mp4\n"
    styles = {text.plain[span.start : span.end]: span.style for span in text.spans}
    assert styles["ffmpeg"] == "cmd.binary"
    assert styles["-i"] == "cmd.flag"
    assert styles["'in put.mkv'"] == "cmd.path"
    assert styles["copy"] == "cmd.value"
