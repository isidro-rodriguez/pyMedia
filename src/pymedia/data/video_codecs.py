"""Datos estáticos de códecs de vídeo y compatibilidad de remux.

La propiedad ``containers`` indica los contenedores en los que FFmpeg puede
codificar el códec. ``remux_containers`` es deliberadamente más conservadora:
contiene únicamente los contenedores que se consideran seguros para copiar los
paquetes con ``-c copy``, sin recodificar.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class VideoCodecData:
    """Configuración e información técnica de un códec de vídeo.

    Attributes:
        name: Nombre normalizado del códec.
        library: Codificador o librería utilizada por FFmpeg.
        containers: Contenedores admitidos para codificación.
        remux_containers: Contenedores seguros para ``-c copy``.
        crf: Rango del Factor de Tasa Constante (mínimo, máximo).
        pix_fmt: Formato de píxeles recomendado.
        presets: Presets disponibles.
        profiles: Perfiles disponibles.
    """

    name: str
    library: str
    containers: tuple[str, ...]
    remux_containers: tuple[str, ...]
    crf: tuple[int, int] | None = None
    pix_fmt: str | None = None
    presets: tuple[str, ...] | None = None
    profiles: tuple[str, ...] | None = None


_VIDEO_CODECS: tuple[VideoCodecData, ...] = (
    VideoCodecData(
        name="av1",
        library="libsvtav1",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".ts", ".webm"),
        remux_containers=(".mkv", ".mp4", ".webm"),
        crf=(0, 63),
        pix_fmt="yuv420p10le",
        presets=tuple(str(value) for value in range(15)),
        profiles=("main", "high", "professional"),
    ),
    VideoCodecData(
        name="dnxhd",
        library="dnxhd",
        containers=(".mkv", ".mov", ".mp4", ".mxf"),
        remux_containers=(".mkv", ".mov", ".mxf"),
    ),
    VideoCodecData(
        name="dvvideo",
        library="dvvideo",
        containers=(".mkv", ".mov", ".mxf"),
        remux_containers=(".mkv", ".mov", ".mxf"),
    ),
    VideoCodecData(
        name="ffv1",
        library="ffv1",
        containers=(".avi", ".mkv", ".mov"),
        remux_containers=(".avi", ".mkv"),
    ),
    VideoCodecData(
        name="flv1",
        library="flv",
        containers=(".f4v", ".flv", ".mkv", ".mov", ".mp4"),
        remux_containers=(".f4v", ".flv", ".mkv"),
    ),
    VideoCodecData(
        name="h261",
        library="h261",
        containers=(".mkv", ".mov", ".mp4"),
        remux_containers=(".mkv", ".mov"),
    ),
    VideoCodecData(
        name="h263",
        library="h263",
        containers=(".3g2", ".3gp", ".f4v", ".flv", ".mkv", ".mov", ".mp4"),
        remux_containers=(".3g2", ".3gp", ".f4v", ".flv", ".mkv", ".mov", ".mp4"),
    ),
    VideoCodecData(
        name="h264",
        library="libx264",
        containers=(
            ".3g2",
            ".3gp",
            ".f4v",
            ".flv",
            ".m2ts",
            ".mkv",
            ".mov",
            ".mp4",
            ".mts",
            ".mxf",
            ".ts",
        ),
        remux_containers=(
            ".3g2",
            ".3gp",
            ".f4v",
            ".flv",
            ".m2ts",
            ".mkv",
            ".mov",
            ".mp4",
            ".mts",
            ".mxf",
            ".ts",
        ),
        crf=(0, 51),
        pix_fmt="yuv420p",
        presets=(
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
            "placebo",
        ),
        profiles=("baseline", "main", "high", "high10"),
    ),
    VideoCodecData(
        name="h265",
        library="libx265",
        containers=(".m2ts", ".mkv", ".mov", ".mp4", ".mts", ".mxf", ".ts"),
        remux_containers=(".m2ts", ".mkv", ".mov", ".mp4", ".mts", ".mxf", ".ts"),
        crf=(0, 51),
        pix_fmt="yuv420p10le",
        presets=(
            "ultrafast",
            "superfast",
            "veryfast",
            "faster",
            "fast",
            "medium",
            "slow",
            "slower",
            "veryslow",
            "placebo",
        ),
        profiles=("main", "main10"),
    ),
    VideoCodecData(
        name="huffyuv",
        library="huffyuv",
        containers=(".avi", ".mkv", ".mov"),
        remux_containers=(".avi", ".mkv", ".mov"),
    ),
    VideoCodecData(
        name="jpeg2000",
        library="jpeg2000",
        containers=(".avi", ".mkv", ".mov", ".mp4"),
        remux_containers=(".avi", ".mkv", ".mov", ".mp4"),
    ),
    VideoCodecData(
        name="mjpeg",
        library="mjpeg",
        containers=(".avi", ".mkv", ".mov", ".mp4", ".ts"),
        remux_containers=(".avi", ".mkv", ".mov", ".mp4", ".ts"),
    ),
    VideoCodecData(
        name="mpeg1video",
        library="mpeg1video",
        containers=(".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".ts", ".vob"),
        remux_containers=(".mkv", ".mov", ".mpeg", ".mpg", ".ts", ".vob"),
    ),
    VideoCodecData(
        name="mpeg2video",
        library="mpeg2video",
        containers=(
            ".m2ts",
            ".mkv",
            ".mov",
            ".mp4",
            ".mpeg",
            ".mpg",
            ".mts",
            ".ts",
            ".vob",
        ),
        remux_containers=(
            ".m2ts",
            ".mkv",
            ".mov",
            ".mpeg",
            ".mpg",
            ".mts",
            ".ts",
            ".vob",
        ),
    ),
    VideoCodecData(
        name="mpeg4",
        library="mpeg4",
        containers=(
            ".3g2",
            ".3gp",
            ".f4v",
            ".flv",
            ".m2ts",
            ".mkv",
            ".mov",
            ".mp4",
            ".mts",
            ".ts",
        ),
        remux_containers=(".3g2", ".3gp", ".f4v", ".flv", ".mkv", ".mov", ".mp4"),
    ),
    VideoCodecData(
        name="msmpeg4v3",
        library="msmpeg4v3",
        containers=(".avi", ".asf", ".wmv"),
        remux_containers=(".avi", ".asf", ".wmv"),
    ),
    VideoCodecData(
        name="prores",
        library="prores",
        containers=(".mkv", ".mov", ".mp4", ".mxf"),
        remux_containers=(".mkv", ".mov", ".mxf"),
    ),
    VideoCodecData(
        name="rawvideo",
        library="rawvideo",
        containers=(".mkv", ".mov", ".mp4"),
        remux_containers=(".mkv", ".mov"),
    ),
    VideoCodecData(
        name="rv40",
        library="rv40",
        containers=(".mkv", ".rm", ".rmvb"),
        remux_containers=(".mkv", ".rm", ".rmvb"),
    ),
    VideoCodecData(
        name="snow",
        library="snow",
        containers=(".mkv",),
        remux_containers=(".mkv",),
    ),
    VideoCodecData(
        name="svq3",
        library="svq3",
        containers=(".mkv", ".mov"),
        remux_containers=(".mkv", ".mov"),
    ),
    VideoCodecData(
        name="theora",
        library="libtheora",
        containers=(".mkv", ".ogg", ".ogv"),
        remux_containers=(".mkv", ".ogg", ".ogv"),
    ),
    VideoCodecData(
        name="utvideo",
        library="utvideo",
        containers=(".avi", ".mkv"),
        remux_containers=(".avi", ".mkv"),
    ),
    VideoCodecData(
        name="vc1",
        library="vc1",
        containers=(".asf", ".avi", ".m2ts", ".mkv", ".mov", ".mp4", ".ts", ".wmv"),
        remux_containers=(".asf", ".avi", ".m2ts", ".mkv", ".ts", ".wmv"),
    ),
    VideoCodecData(
        name="vp6",
        library="vp6",
        containers=(".f4v", ".flv", ".mkv"),
        remux_containers=(".f4v", ".flv", ".mkv"),
    ),
    VideoCodecData(
        name="vp8",
        library="libvpx",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".webm"),
        remux_containers=(".mkv", ".webm"),
    ),
    VideoCodecData(
        name="vp9",
        library="libvpx-vp9",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".webm"),
        remux_containers=(".mkv", ".webm"),
    ),
    VideoCodecData(
        name="wmv1",
        library="wmv1",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
        remux_containers=(".mkv", ".wmv"),
    ),
    VideoCodecData(
        name="wmv2",
        library="wmv2",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
        remux_containers=(".mkv", ".wmv"),
    ),
    VideoCodecData(
        name="wmv3",
        library="wmv3",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
        remux_containers=(".mkv", ".wmv"),
    ),
)


VIDEO_CODECS: Mapping[str, VideoCodecData] = MappingProxyType(
    {codec.name: codec for codec in _VIDEO_CODECS}
)
"""Códecs de vídeo soportados indexados por nombre."""


CODEC_ALIASES: Mapping[str, str] = MappingProxyType(
    {
        "avc": "h264",
        "avc1": "h264",
        "hevc": "h265",
    }
)
"""Nombres habituales de FFmpeg normalizados a los nombres del módulo."""
