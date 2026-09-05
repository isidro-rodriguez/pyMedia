"""Mixins para el procesamiento de la ruta o directorio de salida.

Cada tipo de medio de salida (imagen animada, imagen, subtítulo, ...) tiene
su propio mixin minimalista con un atributo tipado, y delega el cálculo y la
validación de la ruta en las funciones privadas compartidas del módulo.
"""

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
    InvalidArgumentError,
    InvalidContainerError,
    InvalidContainerTypeError,
    MissingMediaPropertyError,
    PermissionDeniedError,
)
from pymedia.locales import _  # noqa
from pymedia.models.media import Media
from pymedia.types import OutputMediaType


class _HasMedia(Protocol):
    """Objeto que expone la ruta y los metadatos del fichero de entrada."""

    media: Media


@dataclass(kw_only=True)
class AnimatedOutputMixin(_HasMedia):
    """Mixin para la ruta de salida de imágenes animadas (GIF).

    Attributes:
        animated_output: Ruta del fichero GIF de salida, o None si aún no
            se ha creado.
    """

    animated_output: Path | None = None

    def create_animated_output(
        self,
        affix: str | None = None,
        extension: str | None = None,
        output: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero GIF de salida.

        Args:
            affix: Sufijo a añadir al nombre del fichero de salida.
            extension: Extensión a forzar en el fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
        """
        self.animated_output = _process_output(
            media=self.media,
            media_type=OutputMediaType.GIF,
            affix=affix,
            extension=extension,
            output=output,
        )


@dataclass(kw_only=True)
class ImageOutputMixin(_HasMedia):
    """Mixin para la ruta o directorio de salida de imágenes.

    Attributes:
        image_output: Ruta del fichero de imagen de salida, válida también
            cuando el lote contiene un único fichero.
        output_directory: Directorio de salida para lotes de varias imágenes.
    """

    image_output: Path | None = None
    output_directory: Path | None = None

    def create_image_output(
        self,
        output: Path | None = None,
        output_directory: Path | None = None,
        affix: str | None = None,
        extension: str | None = None,
    ) -> None:
        """Procesa y asigna la ruta o directorio de salida de la imagen.

        Args:
            output: Ruta de salida explícita, válida solo para lotes de un
                único fichero.
            output_directory: Directorio de salida para lotes de varios ficheros.
            affix: Sufijo a añadir al nombre del fichero de salida.
            extension: Extensión a forzar en el fichero de salida.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)
        self.image_output = _process_output(
            media=self.media,
            media_type=OutputMediaType.IMAGE,
            affix=affix,
            extension=extension,
            output=output,
            output_directory=self.output_directory,
        )


@dataclass(kw_only=True)
class SubtitleOutputMixin(_HasMedia):
    """Mixin para la ruta de salida de subtítulos.

    Attributes:
        subtitle_output: Ruta del fichero de subtítulos de salida, o None si
            aún no se ha creado.
    """

    subtitle_output: Path | None = None

    def create_subtitle_output(
        self,
        affix: str | None = None,
        extension: str | None = None,
        output: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero de subtítulos de salida.

        Args:
            affix: Sufijo a añadir al nombre del fichero de salida.
            extension: Extensión a forzar en el fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
        """
        self.subtitle_output = _process_output(
            media=self.media,
            media_type=OutputMediaType.SUBTITLE,
            affix=affix,
            extension=extension,
            output=output,
        )


def _validate_name(name: str) -> None:
    """Valida que el nombre no contenga caracteres no permitidos."""
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
        raise InvalidArgumentError(
            _(r'%(name)s contains invalid characters: < > : " / \ | ? *')
            % {"name": name}
        )


def _process_output_directory(directory: Path) -> Path:
    """Comprueba y crea la ruta del directorio de salida si no existiese."""
    _validate_name(directory.name)
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise PermissionDeniedError(
            msg=_("Could not create directory: %(path)s") % {"path": directory}
        ) from e
    return directory


def _validate_output(output: Path, media: Media, media_type: OutputMediaType) -> None:
    """Comprueba que la salida tenga una extensión válida para el tipo de medio."""
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
            if output.suffix not in AUDIO_CONTAINERS:
                raise InvalidContainerTypeError(
                    extension=output.suffix,
                    media_type=OutputMediaType.AUDIO.value,
                    supported=",".join(AUDIO_CONTAINERS),
                )
            for audio_track in media.audio:
                if audio_track.codec is None:
                    raise MissingMediaPropertyError(name="audio codec")
                if output.suffix not in AUDIO_CODECS[audio_track.codec].containers:
                    raise InvalidContainerError(
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
            if media.video.codec is None:
                raise MissingMediaPropertyError(name="video codec")
            if output.suffix not in VIDEO_CONTAINERS:
                raise InvalidContainerTypeError(
                    extension=output.suffix,
                    media_type=OutputMediaType.VIDEO.value,
                    supported=",".join(VIDEO_CONTAINERS),
                )
            if output.suffix not in VIDEO_CODECS[media.video.codec].containers:
                raise InvalidContainerError(
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
                    raise InvalidContainerError(
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
    media: Media,
    media_type: OutputMediaType,
    affix: str | None = None,
    extension: str | None = None,
    output: Path | None = None,
    output_directory: Path | None = None,
) -> Path:
    """Procesa la ruta del fichero de salida."""
    if output is not None:
        output = output.absolute()
    else:
        parent = output_directory if output_directory is not None else Path.cwd()
        output = Path(parent / media.path.name).absolute()
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
