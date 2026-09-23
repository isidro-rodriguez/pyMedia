"""Mixins para el procesamiento de la ruta o directorio de salida.

Cada tipo de medio de salida (imagen animada, imagen, subtítulo, ...) tiene
su propio mixin minimalista con un atributo tipado, y delega el cálculo y la
validación de la ruta en las funciones privadas compartidas del módulo.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from types import MappingProxyType

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.subtitles_formats import SUBTITLES_FORMATS
from pymedia.data.supported import SUPPORTED
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import (
    InvalidCodecContainerError,
    InvalidContainerError,
    MissingParameterError,
    MissingPropertyError,
    UserError,
)
from pymedia.locales import _
from pymedia.models.media import Media
from pymedia.types import MediaType


@dataclass(kw_only=True)
class AnimatedOutputMixin:
    """Mixin para la ruta de salida de imágenes animadas.

    Attributes:
        animated_output: Ruta de salida del fichero de imagen animada.
    """

    media: Media | None = None
    animated_output: Path | None = None
    output_directory: Path | None = None

    def create_animated_output(
        self,
        extension: str,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero GIF de salida.

        Args:
            extension: Extensión del fichero de salida.
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de varias imágenes.

        Raises:
            InvalidContainerTypeError: Si la extensión no es una imagen
                animada soportada.
            InvalidArgumentError: Si el nombre de salida contiene caracteres
                no permitidos.
            PermissionDeniedError: Si no se puede crear el directorio de salida.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        media = self.media
        if media is None:
            raise MissingParameterError(name="media")

        output = _process_output(
            media=media,
            affix=affix,
            extension=extension,
            output=output,
            output_directory=self.output_directory,
        )

        if output.suffix not in SUPPORTED.ANIMATED:
            raise InvalidContainerError(
                extension=output.suffix,
                media_type=MediaType.ANIMATED_IMAGE,
                supported=SUPPORTED.ANIMATED,
            )

        self.animated_output = output


@dataclass(kw_only=True)
class AudioOutputMixin:
    """Mixin para la ruta de salida de pistas de audio.

    Attributes:
        audio_output: Ruta de salida del fichero de pista de audio.
        output_directory: Directorio de salida para lotes de varias imágenes.
    """

    media: Media | None = None
    stream_tracks: list[int] | None = None
    audio_output: Path | None = None
    output_directory: Path | None = None

    def create_audio_output(
        self,
        extension: str,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero de pista de audio de salida.

        Valida el contenedor contra las pistas seleccionadas en ``stream_tracks``;
        sin selección, contra todas las pistas de audio de la media.

        Args:
            extension: Extensión del fichero de salida.
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de varios ficheros.

        Raises:
            InvalidContainerTypeError: Si la extensión no es una pista de audio
                soportada.
            MissingPropertyError: Si el medio no tiene pistas de audio o alguna
                no declara códec.
            InvalidContainerError: Si la extensión no soporta el códec de una
                pista.
            InvalidRemuxError: Si el remux de una pista a la extensión no es
                seguro.
            InvalidArgumentError: Si el nombre de salida contiene caracteres
                no permitidos.
            PermissionDeniedError: Si no se puede crear el directorio de salida.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        media = self.media
        if media is None:
            raise MissingParameterError(name="media")

        output = _process_output(
            media=media,
            affix=affix,
            extension=extension,
            output=output,
            output_directory=self.output_directory,
        )

        if output.suffix not in SUPPORTED.AUDIO:
            raise InvalidContainerError(
                extension=output.suffix,
                media_type=MediaType.AUDIO,
                supported=SUPPORTED.AUDIO,
            )

        if media.audio is None:
            raise MissingPropertyError(name="media.audio")
        audio_tracks = media.audio
        # Por defecto se validan todas las pistas; `stream_tracks` la aporta
        # StreamsMixin en el contexto real de los parámetros del comando.
        if self.stream_tracks is not None:
            audio_tracks = [
                track
                for track in media.audio
                if track.track_index in self.stream_tracks
            ]
        for audio_track in audio_tracks:
            if audio_track.codec is None:
                raise MissingPropertyError(name="audio codec")
            codec_data = AUDIO_CODECS[audio_track.codec]
            _validate_remux(
                suffix=output.suffix,
                source_suffix=media.path.suffix,
                codec_name=codec_data.name,
                containers=codec_data.containers,
                remux_containers=codec_data.remux_containers,
            )

        self.audio_output = output


@dataclass(kw_only=True)
class ImageOutputMixin:
    """Mixin para la ruta o directorio de salida de imágenes.

    Attributes:
        image_output: Ruta del fichero de imagen de salida, válida también
            cuando el lote contiene un único fichero.
        output_directory: Directorio de salida para lotes de varias imágenes.
    """

    media: Media | None = None
    image_output: Path | None = None
    output_directory: Path | None = None

    def create_image_output(
        self,
        extension: str,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta o directorio de salida de la imagen.

        Args:
            extension: Extensión del fichero de salida.
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta de salida explícita, no válida solo para lotes.
            output_directory: Directorio de salida para lotes de varios ficheros.

        Raises:
            InvalidContainerTypeError: Si la extensión no es una imagen
                soportada.
            InvalidArgumentError: Si el nombre de salida contiene caracteres
                no permitidos.
            PermissionDeniedError: Si no se puede crear el directorio de salida.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        media = self.media
        if media is None:
            raise MissingParameterError(name="media")

        output = _process_output(
            media=media,
            affix=affix,
            extension=extension,
            output=output,
            output_directory=self.output_directory,
        )

        if output.suffix not in SUPPORTED.IMAGES:
            raise InvalidContainerError(
                extension=output.suffix,
                media_type=MediaType.IMAGE,
                supported=SUPPORTED.IMAGES,
            )

        self.image_output = output


@dataclass(kw_only=True)
class MediaOutputMixin:
    """Mixin para la ruta de salida de contenedores multimedia.

    Attributes:
        media_output: Ruta del fichero contenedor de salida.
        output_directory: Directorio de salida para lotes de varias imágenes.
    """

    media: Media | None = None
    media_output: Path | None = None
    output_directory: Path | None = None

    def create_media_output(
        self,
        extension: str,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
        media_list: list[Media] | None = None,
        remux: bool = False,
    ) -> None:
        """Procesa y asigna la ruta del fichero contenedor multimedia de salida.

        Args:
            extension: Extensión del fichero de salida.
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de varios ficheros.
            media_list: Lista de contenedores multimedia para validar output.
            remux: Indica si es una operación de remux.

        Raises:
            InvalidContainerTypeError: Si la extensión no es un contenedor
                soportado.
            MissingPropertyError: Si falta el vídeo o alguna pista no declara
                su códec.
            InvalidContainerError: Si la extensión no soporta el códec de
                alguna pista del medio.
            InvalidRemuxError: Si el remux de alguna pista a la extensión no
                es seguro.
            InvalidArgumentError: Si el nombre de salida contiene caracteres
                no permitidos.
            PermissionDeniedError: Si no se puede crear el directorio de salida.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        media = self.media if media_list is None else media_list[0]
        if media is None:
            raise MissingParameterError(name="media")

        output = _process_output(
            media=media,
            affix=affix,
            extension=extension,
            output=output,
            output_directory=self.output_directory,
        )

        if media_list is not None:
            _validate_not_input(output=output, inputs=[m.path for m in media_list])

        if media.video is None:
            raise MissingPropertyError(name="video")
        if media.video.codec is None:
            raise MissingPropertyError(name="video codec")

        if output.suffix not in SUPPORTED.CONTAINERS:
            raise InvalidContainerError(
                extension=output.suffix,
                media_type=MediaType.VIDEO,
                supported=SUPPORTED.CONTAINERS,
            )

        if output.suffix not in VIDEO_CODECS[media.video.codec].containers:
            raise InvalidCodecContainerError(
                extension=output.suffix,
                codec=VIDEO_CODECS[media.video.codec].name,
                supported=VIDEO_CODECS[media.video.codec].containers,
            )
        if remux:
            codec = media.video.codec
            _validate_remux(
                suffix=output.suffix,
                source_suffix=media.path.suffix,
                codec_name=codec,
                containers=VIDEO_CODECS[codec].containers,
                remux_containers=VIDEO_CODECS[codec].remux_containers,
            )

        if media.audio is not None:
            for audio_track in media.audio:
                if audio_track.codec is None:
                    raise MissingPropertyError(name="audio codec")
                if output.suffix not in AUDIO_CODECS[audio_track.codec].containers:
                    raise InvalidCodecContainerError(
                        extension=output.suffix,
                        codec=AUDIO_CODECS[audio_track.codec].name,
                        supported=AUDIO_CODECS[audio_track.codec].containers,
                    )
                if remux:
                    codec = audio_track.codec
                    _validate_remux(
                        suffix=output.suffix,
                        source_suffix=media.path.suffix,
                        codec_name=codec,
                        containers=AUDIO_CODECS[codec].containers,
                        remux_containers=AUDIO_CODECS[codec].remux_containers,
                    )

        self.media_output = output

    def to_mp4_cmd_args(self) -> list[str]:
        """Argumentos específicos de contenedores .mp4."""
        if self.media is None:
            raise MissingParameterError(name="media")
        if self.media.video is None:
            raise MissingParameterError(name="video")

        mp4_args = ["-movflags", "+faststart"]
        if self.media.video.codec == "h265":
            mp4_args.extend(["-tag:v", "hvc1"])

        return mp4_args


@dataclass(kw_only=True)
class SubtitlesOutputMixin:
    """Mixin para la ruta de salida de subtítulos.

    Attributes:
        subtitles_output: Ruta del fichero de subtítulos de salida, o None si
            aún no se ha creado.
        output_directory: Directorio de salida para lotes de varias imágenes.
    """

    media: Media | None = None
    stream_tracks: list[int] | None = None
    subtitles_output: Path | None = None
    output_directory: Path | None = None

    def create_subtitles_output(
        self,
        extension: str,
        affix: str | None = None,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Procesa y asigna la ruta del fichero de subtítulos de salida.

        Valida el contenedor contra las pistas seleccionadas en ``stream_tracks``;
        sin selección, contra todas las pistas de subtítulos de la media.

        Args:
            extension: Extensión del fichero de salida.
            affix: Sufijo a añadir al nombre del fichero de salida.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de varios ficheros.

        Raises:
            InvalidContainerTypeError: Si la extensión no es un fichero de
                subtítulos soportado.
            MissingPropertyError: Si el medio no tiene pistas de subtítulos o
                alguna no declara código.
            InvalidContainerError: Si la extensión no soporta el códec de una
                pista.
            InvalidRemuxError: Si el remux de una pista a la extensión no es
                seguro.
            InvalidArgumentError: Si el nombre de salida contiene caracteres
                no permitidos.
            PermissionDeniedError: Si no se puede crear el directorio de salida.
        """
        if output_directory is not None:
            self.output_directory = _process_output_directory(output_directory)

        media = self.media
        if media is None:
            raise MissingParameterError(name="media")

        output = _process_output(
            media=media,
            affix=affix,
            extension=extension,
            output=output,
            output_directory=self.output_directory,
        )

        if output.suffix not in SUPPORTED.SUBTITLES:
            raise InvalidContainerError(
                extension=output.suffix,
                media_type=MediaType.SUBTITLES,
                supported=SUPPORTED.SUBTITLES,
            )

        if media.subtitles is None:
            raise MissingPropertyError(name="media.subtitles")
        subtitles_tracks = media.subtitles
        # Por defecto se validan todas las pistas; `stream_tracks` la aporta
        # StreamsMixin en el contexto real de los parámetros del comando.
        if self.stream_tracks is not None:
            subtitles_tracks = [
                track
                for track in media.subtitles
                if track.track_index in self.stream_tracks
            ]
        for subtitles_track in subtitles_tracks:
            if subtitles_track.codec is None:
                raise MissingPropertyError(name="subtitles codec")
            codec = subtitles_track.codec
            fmt_data = SUBTITLES_FORMATS[
                MappingProxyType({"subrip": "srt"}).get(codec, codec)
            ]
            _validate_remux(
                suffix=output.suffix,
                source_suffix=media.path.suffix,
                codec_name=fmt_data.codec_name,
                containers=fmt_data.containers,
                remux_containers=fmt_data.remux_containers,
            )

        self.subtitles_output = output


def _validate_remux(
    suffix: str,
    source_suffix: str,
    codec_name: str,
    containers: tuple[str, ...],
    remux_containers: tuple[str, ...],
) -> None:
    """Valida el contenedor de salida para una pista sin recodificar."""
    if suffix == source_suffix:
        if suffix not in containers:
            raise InvalidCodecContainerError(
                extension=suffix,
                codec=codec_name,
                supported=containers,
            )
    elif suffix not in remux_containers:
        raise UserError(
            msg=_(
                "Cannot remux %(codec)s to %(extension)s. Safe remux targets: "
                "%(supported)s."
            )
            % {
                "codec": codec_name,
                "extension": suffix,
                "supported": ", ".join(remux_containers),
            },
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
        raise UserError(
            _(r'%(name)s contains invalid characters: < > : " / \ | ? *')
            % {"name": name}
        )


def _process_output_directory(directory: Path) -> Path:
    """Comprueba y crea la ruta del directorio de salida si no existiese."""
    _validate_name(directory.name)
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise UserError(
            msg=_("Could not create directory: %(path)s") % {"path": directory}
        ) from e
    return directory


def _process_output(
    media: Media,
    extension: str,
    affix: str | None = None,
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
        if extension:
            output = output.with_suffix(extension)
    _process_output_directory(output.parent)
    _validate_not_input(output=output, inputs=[media.path])
    return output


def _validate_not_input(output: Path, inputs: list[Path]) -> None:
    """Impide que la salida sea uno de los ficheros de entrada.

    Raises:
        UserError: Si la salida coincide con alguna entrada.
    """
    for source in inputs:
        if output.resolve() == source.resolve():
            raise UserError(
                msg=_("Output file must be different from the input file: %(path)s")
                % {"path": output}
            )
