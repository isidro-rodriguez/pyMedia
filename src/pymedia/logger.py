import logging
import sys
from pathlib import Path

import platformdirs

from pymedia import locales

_configured = False

_LEVEL_ABBREV = {
    "DEBUG": "[DEBUG]",
    "INFO": "[INFO] ",
    "WARNING": "[WARN] ",
    "ERROR": "[ERROR]",
    "CRITICAL": "[CRIT] ",
}


class AbbrevFormatter(logging.Formatter):
    """Formatter que abrevia el levelname (WARNING → [WARN], CRITICAL → [CRIT])."""

    def format(self, record: logging.LogRecord) -> str:
        record.levelname = _LEVEL_ABBREV.get(record.levelname, record.levelname)
        return super().format(record)


class AnsiColorFormatter(AbbrevFormatter):
    def format(self, record: logging.LogRecord) -> str:
        no_style = "\033[0m"
        blue = "\033[34m"
        grey = "\033[90m"
        yellow = "\033[93m"
        red = "\033[31m"
        red_light = "\033[91m"
        start_style = {
            "DEBUG": grey,
            "INFO": blue,
            "WARNING": yellow,
            "ERROR": red,
            "CRITICAL": red_light,
        }.get(record.levelname, no_style)
        end_style = no_style
        return f"{start_style}{super().format(record)}{end_style}"


class PymediaFilter(logging.Filter):
    """Solo deja pasar records del dominio 'pymedia'."""

    def filter(self, record: logging.LogRecord) -> bool:
        return record.name.startswith("pymedia")


def setup_logging(debug: bool = False) -> None:
    """Configura el logger raíz (idempotente).

    - Console handler a stderr (compacto, sin columnas extra)
    - File handler en el directorio de configuración del usuario,
      columnizado para alinear el mensaje.

    Se debe llamar explícitamente una vez desde el entrypoint CLI, pasando
    ``debug=True`` si el usuario pide más verbosidad. Si algún módulo pide
    un logger antes de esa llamada (tests, imports sueltos), se configura
    con el nivel por defecto (INFO) como red de seguridad.
    """
    global _configured
    if _configured:
        return

    level = logging.DEBUG if debug else logging.INFO

    root = logging.getLogger()
    root.setLevel(level)

    console_fmt = AnsiColorFormatter("%(levelname)s %(message)s")
    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(console_fmt)
    console.addFilter(PymediaFilter())
    root.addHandler(console)

    log_path = (
        Path(platformdirs.user_config_dir("pymedia", appauthor=False, roaming=True))
        / "logging.log"
    )
    file_fmt = AbbrevFormatter("%(asctime)s %(levelname)s %(message)s")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(file_fmt)
    file_handler.addFilter(PymediaFilter())
    root.addHandler(file_handler)

    _configured = True


def get_logger(name: str = "", debug: bool = False) -> logging.Logger:
    """Devuelve un logger con prefijo 'pymedia.*'.

    Si `setup_logging()` no se ha llamado todavía (p. ej. en tests o al
    importar un módulo de forma aislada), se configura aquí con el nivel
    por defecto para que el logger siempre esté operativo.
    """
    return logging.getLogger(f"pymedia.{name}" if name else "pymedia")


# -----------------------------------------------------------------------------
#  Helpers con plantillas
# -----------------------------------------------------------------------------


def log_info(logger: logging.Logger, key: str, **kwargs) -> None:
    """Registra un mensaje INFO usando la plantilla de locales.Info."""
    logger.info(locales.Info[key].format(**kwargs))


def log_warning(logger: logging.Logger, key: str, **kwargs) -> None:
    """Registra un mensaje WARNING usando la plantilla de locales.Warnings."""
    logger.warning(locales.Warnings[key].format(**kwargs))


def log_debug(logger: logging.Logger, key: str, **kwargs) -> None:
    """Registra un mensaje DEBUG usando la plantilla de locales.Debug."""
    logger.debug(locales.Debug[key].format(**kwargs))
