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

    def create_input_single(self, input_single: Path) -> None:
        """Crea los atributos input_single y media.

        Attributes
            input_single: Ruta del vídeo a procesar.
        """
        input_single = input_single.absolute()
        self.input_single = input_single
        self.media = _load_media(input_single)

    def to_input_single_cmd(self) -> list[str]:
        """Devuelve lista de str lista para consumo ffmpeg."""
        if self.input_single is None:
            raise MissingParameterError(parameter="input_single")
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

    def create_input_list(self, input_list: list[Path]) -> None:
        """Crea los atributos input_list y media_list."""
        if self.input_list is None:
            raise MissingParameterError(parameter="input_list")
        if self.media_list is None:
            raise MissingParameterError(parameter="media_list")
        for input_single in input_list:
            input_single = input_single.absolute()
            self.input_list.append(input_single)
            self.media_list.append(_load_media(input_single))

    def to_input_list_cmd(self) -> list[str]:
        """Devuelve lista de str lista para consumo ffmpeg."""
        if self.input_list is None:
            raise MissingParameterError(parameter="input_list")
        cmd_list: list[str] = []
        for input_single in self.input_list:
            cmd_list.append("-i")
            cmd_list.append(str(input_single))
        return cmd_list


def _load_media(
    path: Path,
) -> Media:
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
        media: Media = Media.load(path)
    except (
        ValueError,
        subprocess.CalledProcessError,
        JSONDecodeError,
        OSError,
    ) as e:
        raise MissingMediaError(path=str(path)) from e

    return media
