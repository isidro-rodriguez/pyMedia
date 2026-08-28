import subprocess
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path

from pymedia.data.containers import VIDEO_CONTAINERS
from pymedia.errors import (
    InvalidContainerTypeError,
    MissingMediaError,
    MissingParameterError,
)
from pymedia.logger import Logger
from pymedia.models.media import Media


@dataclass(kw_only=True)
class InputSingleMixin:
    """Mixin para recepción individual de inputs de vídeo.

    Attributes:
        input_single: Ruta del fichero de vídeo a procesar.
        media: Metadatos del vídeo.

    Raises:
        MissingMediaError: Si metadatos no obtenidos.
    """

    input_single: Path | None = None
    media: Media | None = None

    def create_input_single(self, input_single: Path, logger: Logger) -> None:
        """Crea los atributos input_single y media.

        Attributes
            input_single: Ruta del vídeo a procesar.
            logger: Sistema de registro de mensajes.

        Raises:
            MissingMediaError: Si metadatos no obtenidos.
            MissingParameterError: Si ruta del fichero no obtenido.
            InvalidContainerTypeError: Si container no válido.
        """
        input_single = input_single.absolute()
        self.input_single = input_single
        self.media = _load_media(path=input_single, logger=logger)

    def to_input_single_cmd(self) -> list[str]:
        """Devuelve lista de str lista para consumo ffmpeg.

        Returns:
            Lista de str lista para consumo ffmpeg.

        Raises:
            MissingParameterError: Si parámetro "input_single" no obtenido.
        """
        if self.input_single is None:
            raise MissingParameterError(name="input_single")
        return ["-i", str(self.input_single)]


@dataclass(kw_only=True)
class InputListMixin:
    """Mixin para recepción de una lista de inputs de vídeo.

    Attributes:
        input_list: Lista de rutas de los ficheros de vídeo a procesar.
        media_list: Lista de metadatos de los vídeos.

    Raises:
        MissingMediaError: Si metadatos no obtenidos.
    """

    input_list: list[Path] | None = None
    media_list: list[Media] | None = None

    def create_input_list(self, input_list: list[Path], logger: Logger) -> None:
        """Crea los atributos input_list y media_list.

        Attributes
            input_single: Ruta del vídeo a procesar.
            logger: Sistema de registro de mensajes.

        Raises:
            MissingMediaError: Si metadatos no obtenidos.
            MissingParameterError: Si ruta del fichero no obtenido.
            InvalidContainerTypeError: Si container no válido.
        """
        inputs: list[Path] = []
        medias: list[Media] = []

        for input_single in input_list:
            input_single = input_single.absolute()
            inputs.append(input_single)
            medias.append(_load_media(path=input_single, logger=logger))

        self.input_list = inputs
        self.media_list = medias

    def to_input_list_cmd(self) -> list[str]:
        """Devuelve lista de str lista para consumo ffmpeg.

        Returns:
            Lista de inputs lista para consumo ffmpeg.

        Raises:
            MissingParameterError: Si parámetro "input_list" no obtenido.
        """
        if self.input_list is None:
            raise MissingParameterError(name="input_list")

        cmd_list: list[str] = []
        for input_single in self.input_list:
            cmd_list.append("-i")
            cmd_list.append(str(input_single))

        return cmd_list


def _load_media(path: Path, logger: Logger) -> Media:
    """Carga la lista de metadatos de los vídeos a procesar"""

    def _validate_video_extension() -> None:
        """Valida que la lista de ficheros tengan extensiones de vídeos."""
        if path.suffix not in VIDEO_CONTAINERS:
            raise InvalidContainerTypeError(
                extension=path.suffix,
                media_type="video",
                supported=", ".join(VIDEO_CONTAINERS),
            )

    _validate_video_extension()

    try:
        media: Media = Media.load(path=path, logger=logger)
    except (
        ValueError,
        subprocess.CalledProcessError,
        JSONDecodeError,
        OSError,
    ) as e:
        raise MissingMediaError(path=str(path)) from e

    return media
