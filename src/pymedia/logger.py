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
from rich.logging import RichHandler
from rich.markup import escape
from rich.pretty import pretty_repr


class Logger:
    """Wrapper sobre logging estándar con plantillas de locales.

    Attributes:
        _configured: Estado de configuración del Logger.
    """

    _configured = False
    _console = Console()

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

        # Handler de Consola con Rich
        console = RichHandler(
            console=cls._console,
            show_time=False,
            show_path=debug,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=debug,
        )
        console.setFormatter(logging.Formatter("%(msg)s"))
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
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel error.

        Args:
            msg: Mensaje ya traducido a mostrar.
            exc_info: Si `True`, añade la traza de la excepción activa.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._log(
            level=logging.ERROR,
            msg=msg,
            console=console,
            file=file,
            exc_info=exc_info,
            values=kwargs,
        )

    def warning(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel aviso (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._log(
            level=logging.WARNING, msg=msg, console=console, file=file, values=kwargs
        )

    def info(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel información (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._log(
            level=logging.INFO, msg=msg, console=console, file=file, values=kwargs
        )

    def debug(
        self,
        msg: str,
        console: bool = True,
        file: bool = True,
        **kwargs: object,
    ) -> None:
        """Muestra log de nivel depuración (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            console: Si `True`, se muestra por consola.
            file: Si `True`, se escribe en el fichero de log.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """

        def _prettify(value: Any) -> object:
            """Convierte en texto multilínea legible y escapa el markup."""
            if isinstance(value, (dict, list, tuple, set)):
                rendered = pretty_repr(_object=value, indent_size=2, expand_all=True)
            else:
                rendered = str(value)
            return escape(rendered)

        kwargs = {name: _prettify(value) for name, value in kwargs.items()}
        self._log(
            level=logging.DEBUG, msg=msg, console=console, file=file, values=kwargs
        )

    def print(self, renderable: RenderableType) -> None:
        """Imprime un objeto Rich (Table, Panel, etc.) por consola.

        Args:
            renderable: Objeto Rich a imprimir (Table, Panel, texto...).
        """
        self._console.print(renderable)

    def _log(
        self,
        level: int,
        msg: str,
        console: bool,
        file: bool,
        *,
        exc_info: bool = False,
        values: dict[str, object] | None = None,
    ) -> None:
        """Envía el registro al logger interno filtrado por destino."""
        self._logger.log(
            level=level,
            msg=self._render(msg=msg, kwargs=values or {}),
            exc_info=exc_info,
            extra={"to_console": console, "to_file": file},
        )

    @staticmethod
    def _render(msg: str, kwargs: dict[str, object]) -> str:
        """Aplica `%(name)s` a `msg` si hay valores que sustituir."""
        if kwargs:
            return msg % kwargs
        return msg


class _DestinationFilter(logging.Filter):
    """Filtra registros según el destino solicitado (consola o fichero)."""

    def __init__(self, key: str) -> None:
        super().__init__()
        self._key = key

    def filter(self, record: logging.LogRecord) -> bool:
        # Si el registro no lleva el flag, se deja pasar por defecto.
        return getattr(record, self._key, True)
