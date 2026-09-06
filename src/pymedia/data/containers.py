"""Datos estáticos de contenedores soportados."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class ContainerData:
    """Representa la configuración e información técnica de un contenedor.

    Esta clase inmutable almacena los códecs compatibles y metadatos
    necesarios para la validación y construcción de comandos de
    remuxado/codificación con FFmpeg.

    Attributes:
        name: Nombre identificador del contenedor (p. ej., 'matroska', 'mp4').
        extension: Extensión de archivo principal, con punto (p. ej., '.mkv').
        mime_type: Tipo MIME asociado (p. ej., 'video/x-matroska').
        video_codecs: Tupla de nombres de códecs de vídeo compatibles. Vacía
            si el contenedor no admite pistas de vídeo.
        audio_codecs: Tupla de nombres de códecs de audio compatibles (deben
            coincidir con las claves de `AUDIO_CODECS`). Vacía si el
            contenedor no admite pistas de audio.
        subtitle_codecs: Tupla de nombres de códecs de subtítulos
            compatibles. Vacía si el contenedor no admite subtítulos.
    """

    name: str
    extension: str
    mime_type: str
    video_codecs: tuple[str, ...] = ()
    audio_codecs: tuple[str, ...] = ()
    subtitle_codecs: tuple[str, ...] = ()


_CONTAINERS: tuple[ContainerData, ...] = (
    ContainerData(
        name="mp4",
        extension=".mp4",
        mime_type="video/mp4",
        video_codecs=("h264", "hevc", "mpeg4", "av1"),
        audio_codecs=("aac", "mp3", "ac3", "eac3"),
        subtitle_codecs=("mov_text",),
    ),
    ContainerData(
        name="matroska",
        extension=".mkv",
        mime_type="video/x-matroska",
        video_codecs=("h264", "hevc", "vp8", "vp9", "av1", "mpeg4", "theora"),
        audio_codecs=(
            "aac",
            "ac3",
            "eac3",
            "flac",
            "mlp",
            "mp2",
            "mp3",
            "opus",
            "truehd",
            "vorbis",
        ),
        subtitle_codecs=("ass", "srt", "hdmv_pgs_subtitle"),
    ),
    ContainerData(
        name="quicktime",
        extension=".mov",
        mime_type="video/quicktime",
        video_codecs=("h264", "hevc", "prores", "mjpeg"),
        audio_codecs=("aac", "alac", "pcm_s16le", "pcm_s24le", "pcm_s32le"),
        subtitle_codecs=("mov_text",),
    ),
    ContainerData(
        name="webm",
        extension=".webm",
        mime_type="video/webm",
        video_codecs=("vp8", "vp9", "av1"),
        audio_codecs=("opus", "vorbis"),
        subtitle_codecs=("webvtt",),
    ),
    ContainerData(
        name="avi",
        extension=".avi",
        mime_type="video/x-msvideo",
        video_codecs=("mpeg4", "h264", "mjpeg"),
        audio_codecs=("mp1", "mp2", "mp3", "pcm_s16le"),
    ),
    ContainerData(
        name="mpegts",
        extension=".ts",
        mime_type="video/mp2t",
        video_codecs=("h264", "hevc"),
        audio_codecs=("aac", "ac3", "eac3", "mp2"),
    ),
    ContainerData(
        name="ogg",
        extension=".ogg",
        mime_type="audio/ogg",
        video_codecs=("theora",),
        audio_codecs=("vorbis", "opus", "flac"),
    ),
    ContainerData(
        name="gif",
        extension=".gif",
        mime_type="image/gif",
        video_codecs=("gif",),
    ),
    ContainerData(
        name="mp3",
        extension=".mp3",
        mime_type="audio/mpeg",
        audio_codecs=("mp3",),
    ),
    ContainerData(
        name="wav",
        extension=".wav",
        mime_type="audio/wav",
        audio_codecs=(
            "pcm_s16le",
            "pcm_s24le",
            "pcm_s32le",
            "pcm_f32le",
            "pcm_alaw",
            "pcm_mulaw",
        ),
    ),
    ContainerData(
        name="flac",
        extension=".flac",
        mime_type="audio/flac",
        audio_codecs=("flac",),
    ),
)

CONTAINERS: Mapping[str, ContainerData] = MappingProxyType(
    {container.extension: container for container in _CONTAINERS}
)
"""dict[str, ContainerData]: Contenedores soportados indexados por extensión."""
