"""Parámetros base compartidos por los comandos."""

from abc import ABC
from dataclasses import dataclass, field

from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class BaseParameters(ABC):
    """Parámetros base.

    Attributes:
        config: Configuración cargada de la aplicación.
        logger: Sistema de registro de mensajes.
        overwrite: Política ante conflicto de salida ya existente.
    """

    config: Config = field(init=False)
    logger: Logger = field(init=False)
    overwrite: OverwriteMode

    def __post_init__(self) -> None:
        """Carga la configuración y el logger al construir los parámetros.

        Se usan campos `init=False` para que las subclases dataclass
        generen un `__init__` que solo acepte sus campos propios, sin
        obligar a pasar `config` y `logger`.
        """
        self.config = Config.load()
        self.logger = Logger.load()
