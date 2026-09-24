"""Mixins de entrada de contenedores multimedia."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.ffprobe import get_media_information
from pymedia.logger import Logger
from pymedia.models.media import Media


@dataclass(kw_only=True)
class MediaInputMixin:
    """Mixin para recepción individual de inputs de vídeo.

    Attributes:
        media: Metadatos del vídeo de entrada ya resuelto y validado.
    """

    media: Media | None = None

    def create_media_input(self, media_input: Path, logger: Logger) -> None:
        """Crea los atributos media_input y media.

        Args:
            media_input: Ruta del fichero de vídeo a procesar.
            logger: Sistema de registro de mensajes.

        Raises:
            InvalidContainerTypeError: Si la extensión del fichero no es un
                contenedor de vídeo soportado.
            MissingParameterError: Si los metadatos del fichero no se pudieron
                mapear.
        """
        self.media = get_media_information(media_input=media_input, logger=logger)

    def to_media_input_cmd(self) -> list[str]:
        """Devuelve la lista de parámetros lista para el consumo de ffmpeg.

        Returns:
            Lista de parámetros lista para el consumo de ffmpeg.

        Raises:
            MissingParameterError: Si no se obtiene el atributo `media`.
        """
        if self.media is None:
            raise MissingParameterError(name="media")

        return ["-i", str(self.media.path)]


@dataclass(kw_only=True)
class MediaListMixin:
    """Mixin para recepción de una lista de inputs de vídeo.

    Attributes:
        media_list: Lista de metadatos de los vídeos a procesar.
    """

    media_list: list[Media] | None = None

    def create_media_list(self, media_input_list: list[Path], logger: Logger) -> None:
        """Crea el atributo media_list con los metadatos de cada vídeo.

        Args:
            media_input_list: Lista de rutas de los ficheros de vídeo a procesar.
            logger: Sistema de registro de mensajes.

        Raises:
            InvalidContainerTypeError: Si extensión no es de contenedor soportado.
            MissingParameterError: Si metadatos de algún fichero no se pudieron mapear.
        """
        media_list: list[Media] = []

        for m in media_input_list:
            media = get_media_information(media_input=m.absolute(), logger=logger)
            media_list.append(media)

        self.media_list = media_list

    def to_media_input_list_cmd(self) -> list[str]:
        """Devuelve la lista de parámetros lista para el consumo de ffmpeg.

        Returns:
            Lista de parámetros lista para el consumo de ffmpeg.

        Raises:
            MissingParameterError: Si no se obtiene el atributo `media_list`.
        """
        if self.media_list is None:
            raise MissingParameterError(name="media_list")

        cmd_list: list[str] = []
        for media in self.media_list:
            cmd_list.append("-i")
            cmd_list.append(str(media.path))

        return cmd_list
