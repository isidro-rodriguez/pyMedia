"""Tema visual de la interfaz de pyMedia.

Define la paleta y los estilos con nombre que usan todas las salidas de Rich
(logs, paneles, tablas, barra de progreso, preguntas y ayuda de Typer). Las
pantallas deben referirse siempre a estos nombres, nunca a colores sueltos.
"""

from rich.theme import Theme

# =============================================================================
#  Paleta
# =============================================================================

PRIMARY = "#16A8F5"
SECONDARY = "#A8C0D9"
SUCCESS = "#00CDBB"
INFO = "#00D9F5"
WARNING = "#FFD21C"
ERROR = "#FF414B"
LIGHT = "#F4F8FF"
DARK = "#0B1628"
DIM = "#647D99"
HIGHLIGHT = "#43E8F5"
BORDER = "#168FE5"
TRACK = "#1C3554"

# =============================================================================
#  Estilos con nombre
# =============================================================================

THEME = Theme(
    {
        # Estados semánticos (estilo Bootstrap)
        "primary": PRIMARY,
        "secondary": SECONDARY,
        "success": SUCCESS,
        "info": INFO,
        "warning": WARNING,
        "error": ERROR,
        "danger": ERROR,
        "light": LIGHT,
        "dark": DARK,
        # Texto
        "text": LIGHT,
        "text.strong": "bold",
        "muted": SECONDARY,
        "dim": DIM,
        "highlight": HIGHLIGHT,
        # Elementos de interfaz
        "border": BORDER,
        "heading": f"bold {PRIMARY}",
        "link": f"underline {INFO}",
        "code": HIGHLIGHT,
        "prompt": f"bold {SUCCESS}",
        # Logs
        "logging.level.debug": SECONDARY,
        "logging.level.info": INFO,
        "logging.level.warning": WARNING,
        "logging.level.error": ERROR,
        "logging.level.critical": f"bold white on {ERROR}",
        # Iconos de los mensajes de log
        "log.debug": DIM,
        "log.info": f"bold {INFO}",
        "log.success": f"bold {SUCCESS}",
        "log.warning": f"bold {WARNING}",
        "log.error": f"bold {ERROR}",
        # Resaltado automático de valores (rutas, números…)
        "repr.path": HIGHLIGHT,
        "repr.filename": f"bold {HIGHLIGHT}",
        "repr.number": INFO,
        "repr.str": SUCCESS,
        "repr.url": f"underline {INFO}",
        "repr.ipv4": INFO,
        "repr.ipv6": INFO,
        "repr.eui48": INFO,
        "repr.eui64": INFO,
        "repr.uuid": SECONDARY,
        "repr.bool_true": f"italic {SUCCESS}",
        "repr.bool_false": f"italic {ERROR}",
        "repr.none": f"italic {DIM}",
        # Tablas y paneles
        "table.header": f"bold {PRIMARY}",
        "table.title": "bold",
        "table.border": BORDER,
        "table.label": SECONDARY,
        "table.na": DIM,
        "table.check": f"bold {SUCCESS}",
        "panel.title": f"bold {PRIMARY}",
        "panel.subtitle": DIM,
        # Barra de progreso
        "progress.description": "",
        "progress.spinner": PRIMARY,
        "progress.percentage": f"bold {INFO}",
        "progress.elapsed": SECONDARY,
        "progress.remaining": SECONDARY,
        "progress.separator": DIM,
        "bar.back": TRACK,
        "bar.complete": PRIMARY,
        "bar.finished": SUCCESS,
        "bar.pulse": HIGHLIGHT,
        # Preguntas
        "prompt.choices": f"bold {INFO}",
        "prompt.default": DIM,
        "prompt.invalid": ERROR,
        "prompt.invalid.choice": ERROR,
        # Comando ffmpeg (--show-cmd)
        "cmd.binary": f"bold {PRIMARY}",
        "cmd.flag": INFO,
        "cmd.value": "",
        "cmd.path": HIGHLIGHT,
        # Ayuda de Typer (ver `pymedia.ui.install_typer_theme`)
        "help.option": f"bold {PRIMARY}",
        "help.switch": f"bold {SUCCESS}",
        "help.negative": f"bold {SECONDARY}",
        "help.metavar": f"bold {WARNING}",
        "help.usage": f"bold {PRIMARY}",
        "help.text": SECONDARY,
        "help.required": ERROR,
        "help.default": DIM,
        "help.command": f"bold {HIGHLIGHT}",
    }
)
