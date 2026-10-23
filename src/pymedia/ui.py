"""Consola y elementos de interfaz compartidos por toda la aplicación.

Toda salida por terminal pasa por `console`, que aplica el tema de
`pymedia.theme`. Así los logs, la barra de progreso, las preguntas y las
tablas comparten estilo y no se pisan entre sí.
"""

import re

import typer
from rich.console import Console
from rich.markup import escape
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeRemainingColumn,
)
from rich.prompt import Confirm
from rich.text import Text
from typer import rich_utils

from pymedia.locales import translate as _
from pymedia.theme import THEME

console = Console(theme=THEME)
"""Consola única de pyMedia, con el tema aplicado."""


class _Confirm(Confirm):
    """Pregunta sí/no con el estilo y los textos de pyMedia."""

    prompt_suffix = " "

    def process_response(self, value: str) -> bool:
        """Acepta `y/yes/s/sí` y `n/no` sin distinguir mayúsculas.

        Raises:
            InvalidResponse: Si la respuesta no es afirmativa ni negativa.
        """
        answer = value.strip().casefold()
        if answer in {"y", "yes", "s", "si", "sí"}:
            return True
        if answer in {"n", "no"}:
            return False
        return super().process_response(value)


def confirm(question: str, default: bool = False) -> bool:
    """Pregunta al usuario una confirmación sí/no con el estilo del tema.

    Args:
        question: Pregunta ya traducida.
        default: Respuesta si el usuario pulsa Intro sin escribir nada.

    Returns:
        `True` si el usuario confirma.

    Raises:
        typer.Abort: Si la entrada se cierra sin respuesta (Ctrl+D, sin stdin).
    """
    prompt = _Confirm(
        Text.assemble(("? ", "prompt"), (question, "text.strong")),
        console=console,
    )
    # Iniciales de "yes"/"no" en el idioma activo; se aceptan también en inglés.
    prompt.choices = [_("y"), _("n")]
    prompt.validate_error_message = "[prompt.invalid]" + _("Please answer y or n.")
    try:
        return prompt(default=default)
    except (EOFError, KeyboardInterrupt) as err:
        console.print()
        raise typer.Abort() from err


# =============================================================================
#  Integración con la ayuda y los errores de Typer
# =============================================================================


def _style(name: str) -> str:
    """Devuelve el estilo del tema como texto, válido fuera de la consola temática."""
    return str(THEME.styles[name])


def install_typer_theme() -> None:
    """Aplica el tema a la ayuda y a los paneles de error que genera Typer.

    Typer crea su propia consola y lee los estilos de constantes del módulo
    `typer.rich_utils`, así que se ajustan antes de construir la aplicación. A
    esa consola se le añade además el tema, para que los textos de ayuda puedan
    usar estilos con nombre (`[heading]`, `[code]`…).
    """
    styles = {
        "STYLE_OPTION": "help.option",
        "STYLE_SWITCH": "help.switch",
        "STYLE_NEGATIVE_OPTION": "help.negative",
        "STYLE_NEGATIVE_SWITCH": "help.negative",
        "STYLE_TYPES": "help.metavar",
        "STYLE_TYPES_SEPARATOR": "dim",
        "STYLE_USAGE": "help.usage",
        "STYLE_USAGE_COMMAND": "text.strong",
        "STYLE_HELPTEXT_FIRST_LINE": "text.strong",
        "STYLE_HELPTEXT": "help.text",
        "STYLE_OPTION_DEFAULT": "help.default",
        "STYLE_REQUIRED_SHORT": "help.required",
        "STYLE_REQUIRED_LONG": "help.required",
        "STYLE_OPTIONS_PANEL_BORDER": "border",
        "STYLE_COMMANDS_PANEL_BORDER": "border",
        "STYLE_COMMANDS_TABLE_FIRST_COLUMN": "help.command",
        "STYLE_ERRORS_PANEL_BORDER": "error",
        "STYLE_ERRORS_SUGGESTION": "dim",
        "STYLE_ABORTED": "warning",
    }
    for constant, name in styles.items():
        setattr(rich_utils, constant, _style(name))

    # Atributo privado de Typer (versión fijada en pyproject.toml).
    setattr(rich_utils, "_get_rich_console", _themed_typer_console)  # noqa: B010


# Fábrica original de Typer, capturada una sola vez al importar el módulo.
_TYPER_CONSOLE_FACTORY = rich_utils._get_rich_console


def _themed_typer_console(stderr: bool = False) -> Console:
    """Consola de Typer con el tema de pyMedia añadido."""
    typer_console = _TYPER_CONSOLE_FACTORY(stderr=stderr)
    typer_console.push_theme(THEME)
    return typer_console


# =============================================================================
#  Barra de progreso
# =============================================================================


def new_progress() -> Progress:
    """Crea la barra de progreso de pyMedia sobre la consola temática.

    Returns:
        `Progress` con icono de estado, descripción, barra, porcentaje y tiempo.
        Con total desconocido la barra muestra una animación continua.
    """
    separator = TextColumn("[progress.separator]•")
    return Progress(
        SpinnerColumn(
            spinner_name="dots",
            style="progress.spinner",
            finished_text=Text("✔", style="log.success"),
        ),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=36),
        TaskProgressColumn(),
        separator,
        # Tiempo restante mientras avanza; el total empleado al terminar.
        TimeRemainingColumn(compact=True, elapsed_when_finished=True),
        console=console,
    )


# =============================================================================
#  Textos de ayuda
# =============================================================================

_EXAMPLE_LINE = re.compile(r"^(?P<indent>\s*)> (?P<command>.+)$", re.MULTILINE)


def styled_help(text: str) -> str:
    """Aplica el tema a un texto de ayuda ya traducido.

    Los textos se escriben con `[bold]` para las cabeceras y líneas
    `> pymedia ...` para los ejemplos; aquí se convierten en estilos del tema
    sin tocar los `msgid` de las traducciones.

    Args:
        text: Texto de ayuda traducido, con markup de Rich.

    Returns:
        Texto con las cabeceras como `heading` y los ejemplos como `code`.

    Examples:
        >>> styled_help("  > pymedia info a.mp4")
        '  [dim]$[/dim] [code]pymedia info a.mp4[/code]'
    """
    text = text.replace("[bold]", "[heading]").replace("[/bold]", "[/heading]")
    return _EXAMPLE_LINE.sub(
        lambda match: (
            f"{match['indent']}[dim]$[/dim] [code]{escape(match['command'])}[/code]"
        ),
        text,
    )
