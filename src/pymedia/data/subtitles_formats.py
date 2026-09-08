"""Datos estáticos de formatos y códecs de subtítulos soportados."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType


class SubtitlesType(Enum):
    """Tipos de subtítulos según su naturaleza de renderizado."""

    TEXT = "text"
    IMAGE = "image"


@dataclass(frozen=True)
class SubtitlesFormatData:
    """Configuración e información técnica de un formato o códec de subtítulos.

    Esta clase inmutable almacena los parámetros necesarios para la
    validación, filtrado y construcción de comandos de subtítulos con FFmpeg.

    Attributes:
        codec_name: Nombre del códec tal como lo reporta ffprobe (p. ej.,
            'srt', 'hdmv_pgs_subtitle'). Es la clave de SUBTITLES_FORMATS.
        library: Nombre de la librería o códec utilizado por FFmpeg al
            construir el comando (p. ej., 'srt', 'pgssub'). Puede diferir
            de codec_name, especialmente en formatos de imagen.
        containers: Tupla con las extensiones de contenedor soportadas (p.
            ej., ('.mkv', '.srt')).
        subtitles_type: Tipo de subtítulos (texto o mapa de bits/imagen).
        supports_styles: Indica si el formato admite estilos avanzados como
            fuentes, colores y posiciones. Por defecto es False.
    """

    codec_name: str
    library: str
    containers: tuple[str, ...]
    subtitles_type: SubtitlesType
    supports_styles: bool = False


_SUBTITLES_FORMATS: tuple[SubtitlesFormatData, ...] = (
    # --- Codecs basados en texto ---
    SubtitlesFormatData(
        codec_name="srt",
        library="srt",
        containers=(".mkv", ".srt"),
        subtitles_type=SubtitlesType.TEXT,
        supports_styles=False,
    ),
    SubtitlesFormatData(
        codec_name="ass",
        library="ass",
        containers=(".mkv", ".ass", ".ssa"),
        subtitles_type=SubtitlesType.TEXT,
        supports_styles=True,  # Soporta fuentes, colores y posiciones complejas
    ),
    SubtitlesFormatData(
        codec_name="webvtt",
        library="webvtt",
        containers=(".mkv", ".webm", ".vtt"),
        subtitles_type=SubtitlesType.TEXT,
        supports_styles=True,
    ),
    SubtitlesFormatData(
        codec_name="mov_text",
        library="mov_text",
        containers=(".mp4", ".mov", ".3gp"),
        subtitles_type=SubtitlesType.TEXT,
        supports_styles=False,  # Subtítulo de texto plano nativo de MP4
    ),
    # --- Codecs basados en imagen (solo lectura / burn-in) ---
    # Los codec_name son los valores oficiales de ffprobe: van en singular.
    SubtitlesFormatData(
        codec_name="dvd_subtitle",
        library="dvdsub",
        containers=(".mkv", ".vob"),
        subtitles_type=SubtitlesType.IMAGE,
        supports_styles=False,
    ),
    SubtitlesFormatData(
        codec_name="hdmv_pgs_subtitle",
        library="pgssub",
        containers=(".mkv", ".m2ts"),
        subtitles_type=SubtitlesType.IMAGE,
        supports_styles=False,
    ),
)

SUBTITLES_FORMATS: Mapping[str, SubtitlesFormatData] = MappingProxyType(
    {fmt.codec_name: fmt for fmt in _SUBTITLES_FORMATS}
)
"""dict[str, SubtitlesFormatData]: Subtítulos indexados por nombre de códec."""
