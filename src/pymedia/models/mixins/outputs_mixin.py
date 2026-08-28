"""Mixins para el procesamiento de la ruta o directorio de salida."""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.containers import (
    ANIMATED_IMAGE_CONTAINERS,
    AUDIO_CONTAINERS,
    OUTPUT_IMAGE_CONTAINERS,
    SUBTITLE_CONTAINERS,
    VIDEO_CONTAINERS,
)
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import (
    CannotCreateDirectoryError,
    ConflictiveOutputParametersError,
    InvalidContainerTypeError,
    InvalidFileExtensionError,
    InvalidNameError,
    MissingMediaPropertyError,
)
from pymedia.models.enums import OutputMediaType
from pymedia.models.media import Media


class _HasSingleMedia(Protocol):
    media: Media
    input_single: Path


class _HasBatchMedia(Protocol):
    media_list: list[Media]
    input_list: list[Path]


@dataclass(kw_only=True)
class OutputSingleMixin(_HasSingleMedia):
    """
    Mixin que gestiona la ruta de salida para comandos de fichero único.

    Attributes:
        output: Ruta del fichero de salida procesada, o None si aún no
            se ha creado.
    """

    output: Path | None = None

    def create_output_single(
        self,
        media_type: OutputMediaType,
        affix: str | None = None,
        extension: str | None = None,
        output: Path | None = None,
    ) -> None:
        """
        Procesa y asigna la ruta de salida a partir de los parámetros de entrada.

        Args:
            media_type: Tipo de medio de salida esperado.
            affix: Sufijo a añadir al nombre del fichero de salida.
            extension: Extensión a forzar en el fichero de salida.
            output: Ruta de salida explícita, si se ha indicado.

        Raises:
            MissingMediaError: Si se indica output sin proporcionar media.
            MissingMediaPropertyError: Si no se pudo obtener un property relevante.
            CannotCreateDirectoryError: Si el usuario no tiene permisos para crear el
                directorio destino.
            InvalidNameError: Si el nombre tiene caracteres inválidos para Windows.
            InvalidFileExtensionError: Si el container no corresponde al códec usado.
            InvalidContainerTypeError: Si el container no corresponde al tipo de medio.
        """
        self.output = _process_output(
            input_single=self.input_single,
            media=self.media,
            media_type=media_type,
            affix=affix,
            extension=extension,
            output=output,
        )


@dataclass(kw_only=True)
class OutputBatchMixin(_HasBatchMedia):
    """
    Mixin que gestiona la ruta o directorio de salida para comandos por lotes.

    Attributes:
        output: Ruta del fichero de salida procesada, válida solo cuando
            el lote contiene un único fichero.
        output_directory: Directorio de salida procesado para lotes de
            varios ficheros.
    """

    output: Path | None = None
    output_directory: Path | None = None

    def create_output_batch(
        self,
        input_single: Path,
        media: Media,
        media_type: OutputMediaType,
        output: Path | None = None,
        output_directory: Path | None = None,
        affix: str | None = None,
        extension: str | None = None,
    ) -> None:
        """
        Procesa y asigna la ruta o directorio de salida para un lote de entradas.

        Args:
            media_type: Tipo de medio de salida esperado.
            output: Ruta de salida explícita, válida solo para lotes de un
                único fichero.
            output_directory: Directorio de salida para lotes de varios
                ficheros.
            affix: Sufijo a añadir al nombre del fichero de salida.
            extension: Extensión a forzar en el fichero de salida.

        Raises:
            ConflictiveOutputParametersError: Si se indican output y
                output_directory a la vez.
            OutputParameterError: Si se indica output con más de un
                fichero de entrada.
            MissingMediaError: Si se indica output sin proporcionar media.
            MissingMediaPropertyError: Si no se pudo obtener un property relevante.
            CannotCreateDirectoryError: Si el usuario no tiene permisos para crear el
                directorio destino.
            InvalidNameError: Si el nombre tiene caracteres inválidos para Windows.
            InvalidFileExtensionError: Si el container no corresponde al códec usado.
            InvalidContainerTypeError: Si el container no corresponde al tipo de medio.
        """
        if output is not None and output_directory is not None:
            raise ConflictiveOutputParametersError()
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)
            return
        self.output = _process_output(
            input_single=input_single,
            media_type=media_type,
            media=media,
            affix=affix,
            extension=extension,
            output=output,
        )


def _validate_name(name: str) -> None:
    """Valida si el archivo o directorio no contiene caracteres no permitidos"""
    invalid_chars = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
    reserved_names = {"CON", "PRN", "AUX", "NUL"} | {
        f"{p}{n}" for p in ("COM", "LPT") for n in range(1, 10)
    }
    if not (
        name
        and not invalid_chars.search(name)
        and not name.endswith((" ", "."))
        and name.upper().split(".")[0] not in reserved_names
    ):
        raise InvalidNameError(filename=name)


def _process_output_directory(directory: Path) -> Path:
    """Comprueba y crea la ruta del directorio de salida si no existiese."""
    _validate_name(directory.name)
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise CannotCreateDirectoryError(path=str(directory)) from e
    return directory


# TODO: validar las pistas de audio como listas en vez de singles
def _validate_output(output: Path, media: Media, media_type: OutputMediaType) -> None:
    """Comprueba el fichero de salida tenga una extensión de animación válida."""

    _process_output_directory(output.parent)
    _validate_name(output.stem)

    match media_type:
        case OutputMediaType.ANIMATED_IMAGE:
            if output.suffix not in ANIMATED_IMAGE_CONTAINERS:
                raise InvalidContainerTypeError(
                    extension=output.suffix,
                    media_type=OutputMediaType.ANIMATED_IMAGE.value,
                    supported=",".join(ANIMATED_IMAGE_CONTAINERS),
                )
        case OutputMediaType.AUDIO:
            if media.audio is None:
                raise MissingMediaPropertyError(name="audio track")
            for audio_track in media.audio:
                if audio_track.codec is None:
                    raise MissingMediaPropertyError(name="audio codec")
            if output.suffix not in AUDIO_CONTAINERS:
                raise InvalidContainerTypeError(
                    extension=output.suffix,
                    media_type=OutputMediaType.AUDIO.value,
                    supported=",".join(AUDIO_CONTAINERS),
                )
            for audio_track in media.audio:
                if output.suffix not in AUDIO_CODECS[audio_track.codec].containers:
                    raise InvalidFileExtensionError(
                        extension=output.suffix,
                        codec=AUDIO_CODECS[audio_track.codec].name,
                        supported=",".join(AUDIO_CODECS[audio_track.codec].containers),
                    )
        case OutputMediaType.IMAGE:
            if output.suffix not in OUTPUT_IMAGE_CONTAINERS:
                raise InvalidContainerTypeError(
                    extension=output.suffix,
                    media_type=OutputMediaType.IMAGE.value,
                    supported=",".join(OUTPUT_IMAGE_CONTAINERS),
                )
        case OutputMediaType.SUBTITLE:
            if output.suffix not in SUBTITLE_CONTAINERS:
                raise InvalidContainerTypeError(
                    extension=output.suffix,
                    media_type=OutputMediaType.SUBTITLE.value,
                    supported=",".join(SUBTITLE_CONTAINERS),
                )
        case OutputMediaType.VIDEO:
            if media.video is None:
                raise MissingMediaPropertyError(name="video")
            if media.video is not None and media.video.codec is None:
                raise MissingMediaPropertyError(name="video codec")
            if output.suffix not in VIDEO_CONTAINERS:
                raise InvalidContainerTypeError(
                    extension=output.suffix,
                    media_type=OutputMediaType.VIDEO.value,
                    supported=",".join(VIDEO_CONTAINERS),
                )
            if output.suffix not in VIDEO_CODECS[media.video.codec].containers:
                raise InvalidFileExtensionError(
                    extension=output.suffix,
                    codec=VIDEO_CODECS[media.video.codec].name,
                    supported=",".join(VIDEO_CODECS[media.video.codec].containers),
                )
            if media.audio is None:
                return
            for audio_track in media.audio:
                if audio_track.codec is None:
                    raise MissingMediaPropertyError(name="audio codec")
                if output.suffix not in AUDIO_CODECS[audio_track.codec].containers:
                    raise InvalidFileExtensionError(
                        extension=output.suffix,
                        codec=AUDIO_CODECS[audio_track.codec].name,
                        supported=",".join(AUDIO_CODECS[audio_track.codec].containers),
                    )
        case OutputMediaType.GIF:
            if output.suffix != ".gif":
                raise InvalidContainerTypeError(
                    extension=output.suffix,
                    media_type="gif files",
                    supported=".gif",
                )


def _process_output(
    input_single: Path,
    media: Media,
    media_type: OutputMediaType,
    affix: str | None = None,
    extension: str | None = None,
    output: Path | None = None,
) -> Path:
    """Procesa la ruta del fichero de salida."""

    if output is not None:
        output = output.absolute()
    else:
        output = Path(Path.cwd() / input_single.name).absolute()
        if affix is not None:
            output = output.with_stem(f"{output.stem}{affix}")
        if extension is not None:
            output = output.with_suffix(extension)

    _validate_output(
        output=output,
        media=media,
        media_type=media_type,
    )

    return output
