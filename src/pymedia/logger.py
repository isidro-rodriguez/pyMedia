"""Servicio de registro de mensajes de pyMedia.

Envuelve el módulo estándar `logging` y lo configura con un handler de consola
Rich y un handler de fichero en el directorio de configuración del usuario.
"""

import logging
from pathlib import Path
from typing import Self

import platformdirs
from rich.console import Console, RenderableType
from rich.logging import RichHandler
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

        console = RichHandler(
            console=cls._console,
            show_time=False,
            show_path=debug,
            markup=True,
            rich_tracebacks=True,
            tracebacks_show_locals=debug,
        )
        console.setFormatter(logging.Formatter("%(msg)s"))
        root.addHandler(console)

        log_path = (
            Path(
                platformdirs.user_config_dir(
                    appname="pymedia", appauthor=False, roaming=True
                )
            )
            / "logging.log"
        )
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(filename=log_path, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)-8s %(msg)s")
        )
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

    def error(self, msg: str, exc_info: bool = False, **kwargs: object) -> None:
        """Muestra log de nivel error.

        Args:
            msg: Mensaje ya traducido a mostrar.
            exc_info: Si `True`, añade la traza de la excepción activa.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._logger.error(self._render(msg, kwargs), exc_info=exc_info)

    def warning(self, msg: str, **kwargs: object) -> None:
        """Muestra log de nivel aviso (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._logger.warning(self._render(msg, kwargs))

    def info(self, msg: str, **kwargs: object) -> None:
        """Muestra log de nivel información (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """
        self._logger.info(self._render(msg, kwargs))

    def debug(self, msg: str, **kwargs: object) -> None:
        """Muestra log de nivel depuración (mensaje ya traducido).

        Args:
            msg: Mensaje ya traducido a mostrar.
            **kwargs: Valores para interpolar en `msg` vía `%`.
        """

        def _prettify(value: object) -> object:
            """Convierte dicts/lists/tuples/sets en texto multilínea legible."""
            if isinstance(value, (dict, list, tuple, set)):
                return pretty_repr(value, indent_size=2, expand_all=True)
            return value

        kwargs = {name: _prettify(value) for name, value in kwargs.items()}
        self._logger.debug(self._render(msg, kwargs))

    def print(self, renderable: RenderableType) -> None:
        """Imprime un objeto Rich (Table, Panel, etc.) por consola.

        Args:
            renderable: Objeto Rich a imprimir (Table, Panel, texto...).
        """
        self._console.print(renderable)

    @staticmethod
    def _render(msg: str, kwargs: dict[str, object]) -> str:
        """Aplica `%(name)s` a `msg` si hay valores que sustituir."""
        if kwargs:
            return msg % kwargs
        return msg
