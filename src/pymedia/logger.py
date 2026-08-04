"""Sistema de logging global de pyMedia."""

import logging
import sys
from pathlib import Path

import platformdirs

_configured = False

_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

_LEVEL_ABBREV = {
    "DEBUG": "DEBUG",
    "INFO": "INFO",
    "WARNING": "WARN",
    "ERROR": "ERROR",
    "CRITICAL": "CRIT",
}


class AbbrevFormatter(logging.Formatter):
    """Formatter que abrevia el levelname (WARNING → WARN, CRITICAL → CRIT)."""

    def format(self, record: logging.LogRecord) -> str:
        record.levelname = _LEVEL_ABBREV.get(record.levelname, record.levelname)
        return super().format(record)


class AnsiColorFormatter(AbbrevFormatter):
    def format(self, record: logging.LogRecord) -> str:
        no_style = "\033[0m"
        blue = "\033[34m"
        bold = "\033[91m"
        grey = "\033[90m"
        yellow = "\033[93m"
        red = "\033[31m"
        red_light = "\033[91m"
        start_style = {
            "DEBUG": grey,
            "INFO": blue,
            "WARNING": yellow,
            "ERROR": red,
            "CRITICAL": red_light + bold,
        }.get(record.levelname, no_style)
        end_style = no_style
        return f"{start_style}{super().format(record)}{end_style}"


def setup_logging() -> None:
    """Configura el logger raíz 'pymedia' (idempotente).

    - Console handler a stderr
    - File handler en el directorio de configuración del usuario,
      o en la ruta indicada si se pasa log_file explícitamente.
    """
    global _configured
    if _configured:
        return

    from pymedia.domain.config import Config

    config = Config.load()
    level = _LEVELS.get(config.app.logger_level.upper(), logging.INFO)

    root = logging.getLogger("pymedia")
    root.setLevel(level)

    fmt = AnsiColorFormatter(
        "[%(levelname)s] %(asctime)s [%(name)s] %(message)s", style="%"
    )

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(fmt)
    root.addHandler(console)

    log_path = (
        Path(platformdirs.user_config_dir("pymedia", appauthor=False, roaming=True))
        / "logging.log"
    )
    file_fmt = AbbrevFormatter(
        "[%(levelname)s] %(asctime)s [%(name)s] %(message)s", style="%"
    )
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(file_fmt)
    root.addHandler(file_handler)

    _configured = True


def get_logger(name: str = "") -> logging.Logger:
    """Devuelve un logger con prefijo 'pymedia.*'."""
    setup_logging()
    return logging.getLogger(f"pymedia.{name}" if name else "pymedia")
