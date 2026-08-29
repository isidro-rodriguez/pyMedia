"""Datos estáticos de códecs de vídeo soportados."""

from collections.abc import Mapping
from dataclasses import dataclass
from types import MappingProxyType


@dataclass(frozen=True)
class VideoCodecData:
    """Representa la configuración e información técnica de un códec de vídeo.

    Esta clase inmutable almacena los parámetros necesarios para la
    validación y construcción de comandos de transcodificación con FFmpeg.

    Attributes:
        name: Nombre identificador del códec (p. ej., 'h264', 'av1').
        library: Nombre del codificador/librería utilizado por FFmpeg
            (p. ej., 'libx264', 'libsvtav1').
        containers: Tuple con las extensiones de contenedor soportadas
            (p. ej., ('.mp4', '.mkv')).
        crf: Rango del Factor de Tasa Constante (mínimo, máximo). Es None si
            el códec no soporta CRF o es de solo lectura.
        pix_fmt: Formato de píxeles por defecto o recomendado
            (p. ej., 'yuv420p', 'yuv420p10le').
        presets: Tuple de presets de velocidad/compresión disponibles.
        profiles: Tuple de perfiles (profiles) soportados por el códec.
    """

    name: str
    library: str
    containers: tuple[str, ...]
    crf: tuple[int, int] | None = None
    pix_fmt: str | None = None
    presets: tuple[str, ...] | None = None
    profiles: tuple[str, ...] | None = None


_VIDEO_CODECS: tuple[VideoCodecData, ...] = (
    VideoCodecData(
        name="av1",
        library="libsvtav1",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".ts", ".webm"),
        crf=(0, 63),
        pix_fmt="yuv420p10le",
        presets=(
            "0",
            "1",
            "2",
            "3",
            "4",
            "5",
            "6",
            "7",
            "8",
            "9",
            "10",
            "11",
            "12",
            "13",
            "14",
        ),
        profiles=("main", "high", "professional"),
    ),
    VideoCodecData(
        name="dnxhd",
        library="dnxhd",
        containers=(".mkv", ".mov", ".mp4", ".mxf"),
    ),
    VideoCodecData(
        name="dvvideo",
        library="dvvideo",
        containers=(".mkv", ".mov", ".mxf"),
    ),
    VideoCodecData(
        name="ffv1",
        library="ffv1",
        containers=(".avi", ".mkv", ".mov"),
    ),
    VideoCodecData(
        name="flv1",
        library="flv",
        containers=(".f4v", ".flv", ".mkv", ".mov", ".mp4"),
    ),
    VideoCodecData(
        name="h261",
        library="h261",
        containers=(".mkv", ".mov", ".mp4"),
    ),
    VideoCodecData(
        name="h263",
        library="h263",
        containers=(".3g2", ".3gp", ".f4v", ".flv", ".mkv", ".mov", ".mp4"),
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
        containers=(
            ".m2ts",
            ".mkv",
            ".mov",
            ".mp4",
            ".mts",
            ".mxf",
            ".ts",
        ),
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
    ),
    VideoCodecData(
        name="jpeg2000",
        library="jpeg2000",
        containers=(".avi", ".mkv", ".mov", ".mp4"),
    ),
    VideoCodecData(
        name="mjpeg",
        library="mjpeg",
        containers=(".avi", ".mkv", ".mov", ".mp4", ".ts"),
    ),
    VideoCodecData(
        name="mpeg1video",
        library="mpeg1video",
        containers=(".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".ts", ".vob"),
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
    ),
    VideoCodecData(
        name="msmpeg4v3",
        library="msmpeg4v3",
        containers=(".avi", ".asf", ".wmv"),
    ),
    VideoCodecData(
        name="prores",
        library="prores",
        containers=(".mkv", ".mov", ".mp4", ".mxf"),
    ),
    VideoCodecData(
        name="rawvideo",
        library="rawvideo",
        containers=(".mkv", ".mov", ".mp4"),
    ),
    VideoCodecData(
        name="rv40",
        library="rv40",
        containers=(".mkv", ".rm", ".rmvb"),
    ),
    VideoCodecData(
        name="snow",
        library="snow",
        containers=(".mkv",),
    ),
    VideoCodecData(
        name="svq3",
        library="svq3",
        containers=(".mkv", ".mov"),
    ),
    VideoCodecData(
        name="theora",
        library="libtheora",
        containers=(".mkv", ".ogg", ".ogv"),
    ),
    VideoCodecData(
        name="utvideo",
        library="utvideo",
        containers=(".avi", ".mkv"),
    ),
    VideoCodecData(
        name="vc1",
        library="vc1",
        containers=(".asf", ".avi", ".m2ts", ".mkv", ".mov", ".mp4", ".ts", ".wmv"),
    ),
    VideoCodecData(
        name="vp6",
        library="vp6",
        containers=(".f4v", ".flv", ".mkv"),
    ),
    VideoCodecData(
        name="vp8",
        library="libvpx",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".webm"),
    ),
    VideoCodecData(
        name="vp9",
        library="libvpx-vp9",
        containers=(".mkv", ".mp4", ".ogg", ".ogv", ".webm"),
    ),
    VideoCodecData(
        name="wmv1",
        library="wmv1",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
    ),
    VideoCodecData(
        name="wmv2",
        library="wmv2",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
    ),
    VideoCodecData(
        name="wmv3",
        library="wmv3",
        containers=(".mkv", ".mov", ".mp4", ".wmv"),
    ),
)

VIDEO_CODECS: Mapping[str, VideoCodecData] = MappingProxyType(
    {codec.name: codec for codec in _VIDEO_CODECS}
)