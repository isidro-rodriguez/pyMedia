"""Mixins de entrada de contenedores multimedia."""

import subprocess
from dataclasses import dataclass
from datetime import timedelta
from json import JSONDecodeError
from pathlib import Path

from pymedia.data.containers import VIDEO_CONTAINERS
from pymedia.errors import (
    InvalidContainerTypeError,
    MissingParameterError,
)
from pymedia.ffmpeg.probe import get_media_metadata
from pymedia.logger import Logger
from pymedia.models.audio import Audio
from pymedia.models.media import Media
from pymedia.models.subtitles import Subtitles
from pymedia.models.video import Video
from pymedia.utils import parse_fraction, to_float, to_int


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
        """
        self.media = _create_media(media_input=media_input, logger=logger)

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
        """
        media_list: list[Media] = []

        for m in media_input_list:
            media = _create_media(media_input=m.absolute(), logger=logger)
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


def _create_media(media_input: Path, logger: Logger) -> "Media":
    """Mapea el JSON de ffprobe a MediaInput."""

    def _validate_media_extension() -> None:
        """Valida que la lista de ficheros tengan extensiones de vídeos."""
        if media_input.suffix not in VIDEO_CONTAINERS:
            raise InvalidContainerTypeError(
                extension=media_input.suffix,
                media_type="video",
                supported=", ".join(VIDEO_CONTAINERS),
            )

    _validate_media_extension()

    data = get_media_metadata(path=media_input, logger=logger)

    video, audio, subtitles = None, None, None
    video_track_index, audio_track_index, subtitles_track_index = 0, 0, 0

    for stream in data.get("streams", []):
        codec_type = stream.get("codec_type")
        tags = stream.get("tags", {})
        language = tags.get("language")

        if codec_type == "video":
            video = Video(
                path=media_input.absolute(),
                global_index=stream.get("index"),
                track_index=video_track_index,
                codec=stream.get("codec_name"),
                width=stream.get("width"),
                height=stream.get("height"),
                fps=parse_fraction(stream.get("avg_frame_rate")),
                bit_rate=to_int(stream.get("bit_rate")),
                pix_fmt=stream.get("pix_fmt"),
                aspect_ratio=stream.get("display_aspect_ratio"),
                profile=stream.get("profile"),
            )
            video_track_index += 1
        elif codec_type == "audio":
            if audio is None:
                audio = []
            audio.append(
                Audio(
                    path=media_input.absolute(),
                    global_index=stream.get("index"),
                    track_index=audio_track_index,
                    codec=stream.get("codec_name"),
                    sample_rate=to_int(stream.get("sample_rate")),
                    channels=stream.get("channels"),
                    channel_layout=stream.get("channel_layout"),
                    bit_rate=to_int(stream.get("bit_rate")),
                    language=language,
                )
            )
            audio_track_index += 1
        elif codec_type == "subtitle":
            if subtitles is None:
                subtitles = []
            disposition = stream.get("disposition", {})
            subtitles.append(
                Subtitles(
                    path=media_input.absolute(),
                    global_index=stream.get("index"),
                    track_index=subtitles_track_index,
                    codec=stream.get("codec_name"),
                    language=language,
                    title=tags.get("title"),
                    forced=bool(disposition.get("forced", 0)),
                    default=bool(disposition.get("default", 0)),
                    hearing_impaired=bool(disposition.get("hearing_impaired", 0)),
                    visual_impaired=bool(disposition.get("visual_impaired", 0)),
                )
            )
            subtitles_track_index += 1

    fmt = data.get("format", {})
    duration_val = to_float(fmt.get("duration"))

    try:
        media = Media(
            path=media_input.absolute(),
            duration=timedelta(seconds=duration_val)
            if duration_val is not None
            else None,
            size=to_int(fmt.get("size")),
            format_name=fmt.get("format_name"),
            video=video,
            audio=audio,
            subtitle=subtitles,
        )
    except (
        ValueError,
        subprocess.CalledProcessError,
        JSONDecodeError,
        OSError,
    ) as e:
        raise MissingParameterError(name="media") from e

    return media
