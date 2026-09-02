"""Pipeline de argumentos y parámetros del subcomando info."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.logger import Logger
from pymedia.models.mixins.inputs_mixin import InputSingleMixin


@dataclass(frozen=True, kw_only=True, slots=True)
class InfoArguments:
    """Argumentos cargados por Typer para el comando Info.

    Attributes:
        input_single: Ruta del fichero de vídeo a procesar.
    """

    input_single: Path


@dataclass(kw_only=True)
class InfoParameters(
    InputSingleMixin,
):
    """Parámetros utilizados por el comando Info.

    Attributes:
        input_single: Ruta del fichero de vídeo a procesar.
        media: Metadatos del vídeo de entrada ya resuelto y validado.
    """

    @classmethod
    def create(cls, args: InfoArguments, logger: Logger) -> "InfoParameters":
        """Crea y valida los parámetros del comando Info desde los argumentos brutos.

        Args:
            args: Argumentos tipados específicos del comando.
            logger: Interfaz principal de la aplicación para generar mensajes.

        Returns:
            Instancia de InfoParameters completamente inicializada.
        """
        params: InfoParameters = InfoParameters()
        params.create_input_single(input_single=args.input_single, logger=logger)
        return params
