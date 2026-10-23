"""Servicio de registro de mensajes de pyMedia.

Envuelve el módulo estándar `logging` y lo configura con un handler de consola
Rich y un handler de fichero en el directorio de configuración del usuario.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Self

import platformdirs
from rich.console import Console, RenderableType
from rich.highlighter import ReprHighlighter
from rich.markup import escape
from rich.pretty import pretty_repr
from rich.table import Table
from rich.text import Text
from rich.traceback import Traceback

from pymedia.ui import console as ui_console

# Icono y estilo de cada nivel en consola; el éxito es un INFO marcado.
_LEVEL_ICONS = {
    logging.DEBUG: ("•", "log.debug"),
    logging.INFO: ("ℹ", "log.info"),
    logging.WARNING: ("▲", "log.warning"),
    logging.ERROR: ("✖", "log.error"),
    logging.CRITICAL: ("✖", "log.error"),
}
_SUCCESS_ICON = ("✔", "log.success")

# Hasta que `Logger.create` configura los destinos, los mensajes no deben llegar
# al manejador de último recurso de logging, que los imprimiría sin formato en
# stderr (p. ej. los `UserError` lanzados al validar argumentos).
logging.getLogger("pymedia").addHandler(logging.NullHandler())


class Logger:
    """Wrapper sobre logging estándar con plantillas de locales.

    Attributes:
        _configured: Estado de configuración del Logger.
    """

    _configured = False
    _console: Console = ui_console

    def __init__(self, logger: logging.Logger) -> None:
        """Inicializa el wrapper sobre un logger estándar.

        Args:
            logger: Interfaz principal de la aplicación para generar mensajes.
        """
        self._logger = logger

    @classmethod
    def create(cls, debug: bool = False) -> Self:
        """Configura el logger raíz (idempotente).

        Args:
            debug: Activa el modo DEBUG.

        Returns:
            Devuelve un Logger con prefijo 'pymedia.*'.
        """
        if cls._configured:
            return cls.load()

        level = logging.DEBUG if debug else logging.INFO
        root = logging.getLogger()
        root.setLevel(level)

        # Handler de consola con el tema de pyMedia
        console = _ConsoleHandler(console=cls._console, debug=debug)
        console.addFilter(_DestinationFilter("to_console"))
        root.addHandler(console)

        # Ruta del archivo de log
        log_path = (
            Path(
                platformdirs.user_config_dir(
                    appname="pymedia", appauthor=False, roaming=True
                )
            )
            / "logging.log"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = TimedRotatingFileHandler(
            filename=log_path,
            when="midnight",  # Rotación cada día a medianoche
            interval=1,  # Intervalo de 1 día
            backupCount=7,  # Mantiene los últimos 7 días de historial
            encoding="utf-8",
        )
        file_handler.suffix = "%Y-%m-%d"

        file_handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s %(levelname)-8s %(msg)s",
                datefmt="%Y-%m-%d %H:%M:%S",  # <-- Sin milisegundos
            )
        )
        file_handler.addFilter(_DestinationFilter("to_file"))
        root.addHandler(file_handler)

        cls._configured = True

        return cls.load()

    @classmethod
    def load(cls, debug: bool = False) -> Self:
        """Devuelve un Logger con prefijo 'pymedia.*'.

        Args:
            debug: Activar nivel de log DEBUG.

        Returns:
            Logger con prefijo 'pymedia.*'.
        """
        if not cls._configured:
            cls.create(debug=debug)
        return cls(logging.getLogger(__name__))

    def error(
        self,
        msg: str,
        exc_info: bool = False,
        console: bool = True,
        file: bool = True,
        markup: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel error.

        Args:
            msg: Mensaje ya traducido a mostrar.
            exc_info: Si `True`, añade la traza de la excepción activa.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            markup: Si `True`, resalta en consola los valores interpolados.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._log(
            level=logging.ERROR,
            msg=msg,
            console=console,
            file=file,
            markup=markup,
            exc_info=exc_info,
            values=kwargs,
        )

    def warning(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        markup: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel aviso (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            markup: Si `True`, resalta en consola los valores interpolados.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._log(
            level=logging.WARNING,
            msg=msg,
            console=console,
            file=file,
            markup=markup,
            values=kwargs,
        )

    def info(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        markup: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel información (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            markup: Si `True`, resalta en consola los valores interpolados.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._log(
            level=logging.INFO,
            msg=msg,
            console=console,
            file=file,
            markup=markup,
            values=kwargs,
        )

    def success(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        markup: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra el resultado satisfactorio de una operación (nivel INFO).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            markup: Si `True`, resalta en consola los valores interpolados.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._log(
            level=logging.INFO,
            msg=msg,
            console=console,
            file=file,
            markup=markup,
            values=kwargs,
            success=True,
        )

    def debug(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        markup: bool = False,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel depuración (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            markup: Si `True`, resalta en consola los valores interpolados.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """

        def _prettify(value: Any) -> object:
            """Convierte las colecciones en texto multilínea legible."""
            if isinstance(value, (dict, list, tuple, set)):
                return pretty_repr(_object=value, indent_size=2, expand_all=True)
            return value

        kwargs = {name: _prettify(value) for name, value in kwargs.items()}
        self._log(
            level=logging.DEBUG,
            msg=msg,
            console=console,
            file=file,
            markup=markup,
            values=kwargs,
        )

    def print(self, renderable: RenderableType, **kwargs: Any) -> None:
        """Imprime un objeto Rich (Table, Panel, etc.) por consola.

        Args:
            renderable: Objeto Rich a imprimir (Table, Panel, texto...).
            **kwargs: Argumentos adicionales para `Console.print`
        """
        self._console.print(renderable, **kwargs)

    def _log(
        self,
        level: int,
        msg: str,
        console: bool,
        file: bool,
        markup: bool,
        *,
        exc_info: bool = False,
        values: dict[str, object] | None = None,
        success: bool = False,
    ) -> None:
        """Envía el registro al logger interno filtrado por destino.

        El fichero recibe el texto plano; la consola, la versión con estilos en
        la que los valores interpolados se resaltan.
        """
        values = values or {}
        plain = self._render(msg=msg, kwargs=values)
        rich_msg = _render_markup(msg, values) if markup else escape(plain)
        self._logger.log(
            level=level,
            msg=plain,
            exc_info=exc_info,
            extra={
                "to_console": console,
                "to_file": file,
                "rich_msg": rich_msg,
                "success": success,
            },
        )

    @staticmethod
    def _render(msg: str, kwargs: dict[str, object]) -> str:
        """Aplica `%(name)s` a `msg` si hay valores que sustituir."""
        if kwargs:
            return msg % kwargs
        return msg


def _render_markup(msg: str, values: dict[str, object]) -> str:
    """Convierte el mensaje en markup seguro con los valores interpolados resaltados.

    Los textos traducidos no llevan markup: se escapan para que corchetes como
    `[https://...]` se muestren tal cual.
    """
    if not values:
        return escape(msg)
    return escape(msg) % {
        name: f"[highlight]{escape(str(value))}[/]" for name, value in values.items()
    }


class _ConsoleHandler(logging.Handler):
    """Muestra cada registro como `icono mensaje` con el tema de pyMedia."""

    def __init__(self, console: Console, debug: bool) -> None:
        """Inicializa el handler.

        Args:
            console: Consola temática donde escribir.
            debug: Si `True`, las trazas incluyen variables locales.
        """
        super().__init__()
        self._console = console
        self._debug = debug
        self._highlighter = ReprHighlighter()

    def emit(self, record: logging.LogRecord) -> None:
        """Escribe el registro en consola; los fallos se delegan en `handleError`."""
        try:
            self._console.print(self._render(record))
            if record.exc_info and record.exc_info[1] is not None:
                exc_type, exc_value, traceback = record.exc_info
                self._console.print(
                    Traceback.from_exception(
                        exc_type, exc_value, traceback, show_locals=self._debug
                    )
                )
        except Exception:  # noqa: BLE001 - contrato de logging.Handler
            self.handleError(record)

    def _render(self, record: logging.LogRecord) -> Table:
        """Compone el icono y el mensaje alineando las líneas de continuación."""
        icon, style = (
            _SUCCESS_ICON
            if getattr(record, "success", False)
            else _LEVEL_ICONS.get(record.levelno, _LEVEL_ICONS[logging.INFO])
        )
        rich_msg = getattr(record, "rich_msg", None)
        text = Text.from_markup(rich_msg) if rich_msg is not None else Text(record.msg)
        # El cuerpo usa el color del terminal para leerse en fondos claros y oscuros.
        text.style = "dim" if record.levelno == logging.DEBUG else ""
        grid = Table.grid(padding=(0, 1))
        grid.add_column(width=1, no_wrap=True)
        grid.add_column(overflow="fold")
        grid.add_row(Text(icon, style=style), self._highlighter(text))
        return grid


class _DestinationFilter(logging.Filter):
    """Filtra registros según el destino solicitado (consola o fichero)."""

    def __init__(self, key: str) -> None:
        super().__init__()
        self._key = key

    def filter(self, record: logging.LogRecord) -> bool:
        # Si el registro no lleva el flag, se deja pasar por defecto.
        return getattr(record, self._key, True)
