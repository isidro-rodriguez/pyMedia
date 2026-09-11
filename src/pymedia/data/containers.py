"""Catálogo completo de contenedores multimedia para validaciones.

Define :class:`ContainerData` y el mapeo :data:`CONTAINERS` indexado por
extensión. Es la fuente de verdad de qué códecs de vídeo, audio y
subtítulos admite cada contenedor, y sirve para validar entradas y para
los tests de coherencia con los catálogos de códecs.

Relación con otros catálogos:
- ``supported.py`` lista únicamente los contenedores que la aplicación
  soporta como destino de conversión; este catálogo es más amplio.
- Los formatos de imagen estática y animada se catalogan en
  ``image_formats.py`` y ``animated_image_formats.py``.

Nota sobre nombres de códec: las claves de ``video_codecs`` son las
canónicas de ``VIDEO_CODECS``; p. ej., el HEVC que ffprobe reporta como
``hevc`` corresponde a la clave ``h265``.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class ContainerData:
    """Información de un contenedor multimedia.

    Attributes:
        name: Nombre identificador del contenedor.
        extension: Extensión de archivo con el punto (p. ej., '.mp4').
        mime_type: Tipo MIME principal del contenedor.
        video_codecs: Claves de ``VIDEO_CODECS`` admitidas como pistas de
            vídeo. Vacía si el contenedor no admite vídeo.
        audio_codecs: Claves de ``AUDIO_CODECS`` admitidas como pistas de
            audio. Vacía si el contenedor no admite audio.
        subtitles_codecs: Claves de ``SUBTITLES_FORMATS`` admitidas. Vacía
            si el contenedor no admite subtítulos.
    """

    name: str
    extension: str
    mime_type: str
    video_codecs: tuple[str, ...] = ()
    audio_codecs: tuple[str, ...] = ()
    subtitles_codecs: tuple[str, ...] = ()


_CONTAINERS: tuple[ContainerData, ...] = (
    ContainerData(
        name="3gpp2",
        extension=".3g2",
        mime_type="video/3gpp2",
        video_codecs=("h263", "h264", "mpeg4"),
    ),
    ContainerData(
        name="3gpp",
        extension=".3gp",
        mime_type="video/3gpp",
        video_codecs=("h263", "h264", "mpeg4"),
        audio_codecs=("amr_nb", "amr_wb"),
        subtitles_codecs=("mov_text",),
    ),
    ContainerData(
        name="ac3",
        extension=".ac3",
        mime_type="audio/ac3",
        audio_codecs=("ac3",),
    ),
    ContainerData(
        name="aiff",
        extension=".aiff",
        mime_type="audio/aiff",
        audio_codecs=("pcm_f32le", "pcm_s16le", "pcm_s24le", "pcm_s32le"),
    ),
    ContainerData(
        name="amr",
        extension=".amr",
        mime_type="audio/amr",
        audio_codecs=("amr_nb",),
    ),
    ContainerData(
        name="asf",
        extension=".asf",
        mime_type="video/x-ms-asf",
        video_codecs=("msmpeg4v3", "vc1"),
    ),
    ContainerData(
        name="ass",
        extension=".ass",
        mime_type="text/x-ssa",
        subtitles_codecs=("ass",),
    ),
    ContainerData(
        name="au",
        extension=".au",
        mime_type="audio/basic",
        audio_codecs=("pcm_alaw", "pcm_mulaw"),
    ),
    ContainerData(
        name="avi",
        extension=".avi",
        mime_type="video/x-msvideo",
        video_codecs=(
            "ffv1",
            "huffyuv",
            "jpeg2000",
            "mjpeg",
            "msmpeg4v3",
            "utvideo",
            "vc1",
        ),
        audio_codecs=("adpcm_ms", "mp1", "mp2", "pcm_s16le"),
    ),
    ContainerData(
        name="awb",
        extension=".awb",
        mime_type="audio/amr-wb",
        audio_codecs=("amr_wb",),
    ),
    ContainerData(
        name="f4v",
        extension=".f4v",
        mime_type="video/x-f4v",
        video_codecs=("flv1", "h263", "h264", "mpeg4", "vp6"),
    ),
    ContainerData(
        name="flac",
        extension=".flac",
        mime_type="audio/flac",
        audio_codecs=("flac", "pcm_s24le"),
    ),
    ContainerData(
        name="flv",
        extension=".flv",
        mime_type="video/x-flv",
        video_codecs=("flv1", "h263", "h264", "mpeg4", "vp6"),
    ),
    ContainerData(
        name="gif",
        extension=".gif",
        mime_type="image/gif",
    ),
    ContainerData(
        name="m2ts",
        extension=".m2ts",
        mime_type="video/mp2t",
        video_codecs=("h264", "h265", "mpeg2video", "mpeg4", "vc1"),
        audio_codecs=("ac3", "eac3", "truehd"),
        subtitles_codecs=("hdmv_pgs_subtitle",),
    ),
    ContainerData(
        name="m4a",
        extension=".m4a",
        mime_type="audio/mp4",
        audio_codecs=("aac", "alac"),
    ),
    ContainerData(
        name="mka",
        extension=".mka",
        mime_type="audio/x-matroska",
        audio_codecs=(
            "aac",
            "ac3",
            "alac",
            "eac3",
            "flac",
            "mlp",
            "mp3",
            "opus",
            "truehd",
            "vorbis",
        ),
    ),
    ContainerData(
        name="matroska",
        extension=".mkv",
        mime_type="video/x-matroska",
        video_codecs=(
            "av1",
            "dnxhd",
            "dvvideo",
            "ffv1",
            "flv1",
            "h261",
            "h263",
            "h264",
            "h265",
            "huffyuv",
            "jpeg2000",
            "mjpeg",
            "mpeg1video",
            "mpeg2video",
            "mpeg4",
            "prores",
            "rawvideo",
            "rv40",
            "snow",
            "svq3",
            "theora",
            "utvideo",
            "vc1",
            "vp6",
            "vp8",
            "vp9",
            "wmv1",
            "wmv2",
            "wmv3",
        ),
        audio_codecs=(
            "aac",
            "ac3",
            "alac",
            "eac3",
            "flac",
            "mlp",
            "mp1",
            "mp2",
            "mp3",
            "opus",
            "pcm_alaw",
            "pcm_f32le",
            "pcm_mulaw",
            "pcm_s16le",
            "pcm_s24le",
            "pcm_s32le",
            "truehd",
            "vorbis",
        ),
        subtitles_codecs=(
            "ass",
            "dvd_subtitle",
            "hdmv_pgs_subtitle",
            "srt",
            "webvtt",
        ),
    ),
    ContainerData(
        name="mlp",
        extension=".mlp",
        mime_type="audio/vnd.dolby.mlp",
        audio_codecs=("mlp",),
    ),
    ContainerData(
        name="mov",
        extension=".mov",
        mime_type="video/quicktime",
        video_codecs=(
            "dnxhd",
            "dvvideo",
            "ffv1",
            "flv1",
            "h261",
            "h263",
            "h264",
            "h265",
            "huffyuv",
            "jpeg2000",
            "mjpeg",
            "mpeg1video",
            "mpeg2video",
            "mpeg4",
            "prores",
            "rawvideo",
            "svq3",
            "vc1",
            "wmv1",
            "wmv2",
            "wmv3",
        ),
        audio_codecs=(
            "aac",
            "alac",
            "mp1",
            "pcm_alaw",
            "pcm_f32le",
            "pcm_mulaw",
            "pcm_s16le",
            "pcm_s24le",
            "pcm_s32le",
        ),
        subtitles_codecs=("mov_text",),
    ),
    ContainerData(
        name="mp1",
        extension=".mp1",
        mime_type="audio/mpeg",
        audio_codecs=("mp1",),
    ),
    ContainerData(
        name="mp2",
        extension=".mp2",
        mime_type="audio/mpeg",
        audio_codecs=("mp2",),
    ),
    ContainerData(
        name="mp3",
        extension=".mp3",
        mime_type="audio/mpeg",
        audio_codecs=("mp3",),
    ),
    ContainerData(
        name="mp4",
        extension=".mp4",
        mime_type="video/mp4",
        video_codecs=(
            "av1",
            "dnxhd",
            "flv1",
            "h261",
            "h263",
            "h264",
            "h265",
            "jpeg2000",
            "mjpeg",
            "mpeg1video",
            "mpeg2video",
            "mpeg4",
            "prores",
            "rawvideo",
            "vc1",
            "vp8",
            "vp9",
            "wmv1",
            "wmv2",
            "wmv3",
        ),
        audio_codecs=("aac", "alac", "eac3", "opus"),
        subtitles_codecs=("mov_text",),
    ),
    ContainerData(
        name="mpeg",
        extension=".mpeg",
        mime_type="video/mpeg",
        video_codecs=("mpeg1video", "mpeg2video"),
        audio_codecs=("mp2",),
    ),
    ContainerData(
        name="mpg",
        extension=".mpg",
        mime_type="video/mpeg",
        video_codecs=("mpeg1video", "mpeg2video"),
        audio_codecs=("mp2",),
    ),
    ContainerData(
        name="mts",
        extension=".mts",
        mime_type="video/mp2t",
        video_codecs=("h264", "h265", "mpeg2video", "mpeg4"),
    ),
    ContainerData(
        name="mxf",
        extension=".mxf",
        mime_type="application/mxf",
        video_codecs=("dnxhd", "dvvideo", "h264", "h265", "prores"),
    ),
    ContainerData(
        name="oga",
        extension=".oga",
        mime_type="audio/ogg",
        audio_codecs=("vorbis",),
    ),
    ContainerData(
        name="ogg",
        extension=".ogg",
        mime_type="audio/ogg",
        video_codecs=("av1", "theora", "vp8", "vp9"),
        audio_codecs=("flac", "opus", "vorbis"),
    ),
    ContainerData(
        name="ogv",
        extension=".ogv",
        mime_type="video/ogg",
        video_codecs=("av1", "theora", "vp8", "vp9"),
    ),
    ContainerData(
        name="opus",
        extension=".opus",
        mime_type="audio/opus",
        audio_codecs=("opus",),
    ),
    ContainerData(
        name="raw",
        extension=".raw",
        mime_type="audio/x-raw",
        audio_codecs=(
            "pcm_alaw",
            "pcm_f32le",
            "pcm_mulaw",
            "pcm_s16le",
            "pcm_s24le",
            "pcm_s32le",
        ),
    ),
    ContainerData(
        name="rm",
        extension=".rm",
        mime_type="application/vnd.rn-realmedia",
        video_codecs=("rv40",),
    ),
    ContainerData(
        name="rmvb",
        extension=".rmvb",
        mime_type="application/vnd.rn-realmedia-vbr",
        video_codecs=("rv40",),
    ),
    ContainerData(
        name="rtp",
        extension=".rtp",
        mime_type="application/octet-stream",
        audio_codecs=("pcm_alaw", "pcm_mulaw"),
    ),
    ContainerData(
        name="srt",
        extension=".srt",
        mime_type="application/x-subrip",
        subtitles_codecs=("srt",),
    ),
    ContainerData(
        name="ssa",
        extension=".ssa",
        mime_type="text/x-ssa",
        subtitles_codecs=("ass",),
    ),
    ContainerData(
        name="thd",
        extension=".thd",
        mime_type="audio/vnd.dolby.mlp",
        audio_codecs=("truehd",),
    ),
    ContainerData(
        name="ts",
        extension=".ts",
        mime_type="video/mp2t",
        video_codecs=(
            "av1",
            "h264",
            "h265",
            "mjpeg",
            "mpeg1video",
            "mpeg2video",
            "mpeg4",
            "vc1",
        ),
        audio_codecs=("aac", "ac3", "eac3", "mp2"),
    ),
    ContainerData(
        name="vob",
        extension=".vob",
        mime_type="video/mpeg",
        video_codecs=("mpeg1video", "mpeg2video"),
        audio_codecs=("mp2",),
        subtitles_codecs=("dvd_subtitle",),
    ),
    ContainerData(
        name="webvtt",
        extension=".vtt",
        mime_type="text/vtt",
        subtitles_codecs=("webvtt",),
    ),
    ContainerData(
        name="wav",
        extension=".wav",
        mime_type="audio/wav",
        audio_codecs=(
            "pcm_alaw",
            "pcm_f32le",
            "pcm_mulaw",
            "pcm_s16le",
            "pcm_s24le",
            "pcm_s32le",
        ),
    ),
    ContainerData(
        name="webm",
        extension=".webm",
        mime_type="video/webm",
        video_codecs=("av1", "vp8", "vp9"),
        audio_codecs=("opus", "vorbis"),
        subtitles_codecs=("webvtt",),
    ),
    ContainerData(
        name="wmv",
        extension=".wmv",
        mime_type="video/x-ms-wmv",
        video_codecs=("msmpeg4v3", "vc1", "wmv1", "wmv2", "wmv3"),
    ),
)


_EXTENSIONS = [container.extension for container in _CONTAINERS]
if len(_EXTENSIONS) != len(set(_EXTENSIONS)):
    raise ValueError("Extensión de contenedor duplicada en el catálogo")

_NAMES = [container.name for container in _CONTAINERS]
if len(_NAMES) != len(set(_NAMES)):
    raise ValueError("Nombre de contenedor duplicado en el catálogo")


CONTAINERS: Mapping[str, ContainerData] = MappingProxyType(
    {container.extension: container for container in _CONTAINERS}
)
"""dict[str, ContainerData]: Contenedores indexados por extensión."""

VIDEO_CONTAINERS: tuple[str, ...] = tuple(
    container.extension for container in _CONTAINERS if container.video_codecs
)
"""tuple[str, ...]: Extensiones de contenedores que admiten pistas de vídeo."""

AUDIO_CONTAINERS: tuple[str, ...] = tuple(
    container.extension for container in _CONTAINERS if container.audio_codecs
)
"""tuple[str, ...]: Extensiones de contenedores que admiten pistas de audio."""

SUBTITLES_CONTAINERS: tuple[str, ...] = tuple(
    container.extension for container in _CONTAINERS if container.subtitles_codecs
)
"""tuple[str, ...]: Extensiones de contenedores que admiten subtítulos."""
