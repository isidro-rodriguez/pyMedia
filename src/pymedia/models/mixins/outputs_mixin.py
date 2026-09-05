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
from pymedia.data.supported import (
    SUPPORTED_ANIMATED,
    SUPPORTED_AUDIO,
    SUPPORTED_IMAGES,
    SUPPORTED_MEDIA,
    SUPPORTED_SUBTITLES,
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
    """Mixin para la ruta de salida de imágenes animadas.

    Attributes:
        animated_output: Ruta de salida del fichero de imagen animada.
    """

    animated_output: Path | None = None
    output_directory: Path | None = None

    def create_animated_output(
        self,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero GIF de salida.

        Args:
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de varias imágenes.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        output = _process_output(
            media=self.media,
            affix=affix,
            extension=".gif",
            output=output,
            output_directory=self.output_directory,
        )

        if output.suffix not in SUPPORTED_ANIMATED:
            raise InvalidContainerTypeError(
                extension=output.suffix,
                media_type=_("animated images"),
                supported=", ".join(SUPPORTED_ANIMATED),
            )

        self.animated_output = output


@dataclass(kw_only=True)
class AudioOutputMixin(_HasMedia):
    """Mixin para la ruta de salida de pistas de audio.

    Attributes:
        audio_output: Ruta de salida del fichero de pista de audio.
        output_directory: Directorio de salida para lotes de varias imágenes.
    """

    audio_output: Path | None = None
    output_directory: Path | None = None

    def create_audio_output(
        self,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero de subtítulos de salida.

        Args:
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de varios ficheros.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        output = _process_output(
            media=self.media,
            affix=affix,
            extension=".m4a",
            output=output,
            output_directory=self.output_directory,
        )

        if output.suffix not in SUPPORTED_AUDIO:
            raise InvalidContainerTypeError(
                extension=output.suffix,
                media_type=OutputMediaType.AUDIO.value,
                supported=",".join(SUPPORTED_AUDIO),
            )

        if self.media is not None:
            if self.media.audio is None:
                raise MissingMediaPropertyError(name="media.audio")
            for audio_track in self.media.audio:
                if audio_track.codec is None:
                    raise MissingMediaPropertyError(name="audio codec")
                if output.suffix not in AUDIO_CODECS[audio_track.codec].containers:
                    raise InvalidContainerError(
                        extension=output.suffix,
                        codec=AUDIO_CODECS[audio_track.codec].name,
                        supported=",".join(AUDIO_CODECS[audio_track.codec].containers),
                    )

        self.audio_output = output


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
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta o directorio de salida de la imagen.

        Args:
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta de salida explícita, no válida solo para lotes.
            output_directory: Directorio de salida para lotes de varios ficheros.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        output = _process_output(
            media=self.media,
            affix=affix,
            extension=".jpg",
            output=output,
            output_directory=self.output_directory,
        )

        if output.suffix not in SUPPORTED_IMAGES:
            raise InvalidContainerTypeError(
                extension=output.suffix,
                media_type=OutputMediaType.IMAGE.value,
                supported=", ".join(SUPPORTED_IMAGES),
            )

        self.image_output = output


@dataclass(kw_only=True)
class MediaOutputMixin(_HasMedia):
    """Mixin para la ruta de salida de contenedores multimedia.

    Attributes:
        media_output: Ruta del fichero contenedor de salida.
        output_directory: Directorio de salida para lotes de varias imágenes.
    """

    media_output: Path | None = None
    output_directory: Path | None = None

    def create_media_output(
        self,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero de subtítulos de salida.

        Args:
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de varios ficheros.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        output = _process_output(
            media=self.media,
            affix=affix,
            extension=".mkv",
            output=output,
            output_directory=self.output_directory,
        )

        if self.media.video is None:
            raise MissingMediaPropertyError(name="video")
        if self.media.video.codec is None:
            raise MissingMediaPropertyError(name="video codec")

        if output.suffix not in SUPPORTED_MEDIA:
            raise InvalidContainerTypeError(
                extension=output.suffix,
                media_type=OutputMediaType.VIDEO.value,
                supported=",".join(SUPPORTED_MEDIA),
            )

        if output.suffix not in VIDEO_CODECS[self.media.video.codec].containers:
            raise InvalidContainerError(
                extension=output.suffix,
                codec=VIDEO_CODECS[self.media.video.codec].name,
                supported=",".join(VIDEO_CODECS[self.media.video.codec].containers),
            )

        if self.media.audio is not None:
            for audio_track in self.media.audio:
                if audio_track.codec is None:
                    raise MissingMediaPropertyError(name="audio codec")
                if output.suffix not in AUDIO_CODECS[audio_track.codec].containers:
                    raise InvalidContainerError(
                        extension=output.suffix,
                        codec=AUDIO_CODECS[audio_track.codec].name,
                        supported=",".join(AUDIO_CODECS[audio_track.codec].containers),
                    )

        self.media_output = output


@dataclass(kw_only=True)
class SubtitleOutputMixin(_HasMedia):
    """Mixin para la ruta de salida de subtítulos.

    Attributes:
        subtitle_output: Ruta del fichero de subtítulos de salida, o None si
            aún no se ha creado.
        output_directory: Directorio de salida para lotes de varias imágenes.
    """

    subtitle_output: Path | None = None
    output_directory: Path | None = None

    def create_subtitle_output(
        self,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero de subtítulos de salida.

        Args:
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de varios ficheros.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        output = _process_output(
            media=self.media,
            affix=affix,
            extension=".srt",
            output=output,
            output_directory=self.output_directory,
        )

        if output.suffix not in SUPPORTED_SUBTITLES:
            raise InvalidContainerTypeError(
                extension=output.suffix,
                media_type=_("subtitle files"),
                supported=", ".join(SUPPORTED_SUBTITLES),
            )

        self.subtitle_output = output


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


def _process_output(
    media: Media,
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

    return output
