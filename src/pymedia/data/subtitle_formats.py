"""Datos estáticos de formatos y códecs de subtítulos soportados."""

from collections.abc import Mapping
from dataclasses import dataclass
from enum import Enum
from types import MappingProxyType


class SubtitleType(Enum):
    """Tipos de subtítulos según su naturaleza de renderizado."""

    TEXT = "text"
    IMAGE = "image"


@dataclass(frozen=True)
class SubtitleFormatData:
    """Configuración e información técnica de un formato o códec de subtítulos.

    Esta clase inmutable almacena los parámetros necesarios para la
    validación, filtrado y construcción de comandos de subtítulos con FFmpeg.

    Attributes:
        codec_name: Nombre del códec tal como lo reporta ffprobe (p. ej.,
            'srt', 'hdmv_pgs_subtitle'). Es la clave de SUBTITLE_FORMATS.
        library: Nombre de la librería o códec utilizado por FFmpeg al
            construir el comando (p. ej., 'srt', 'pgssub'). Puede diferir
            de codec_name, especialmente en formatos de imagen.
        containers: Tupla con las extensiones de contenedor soportadas (p.
            ej., ('.mkv', '.srt')).
        sub_type: Tipo de subtítulo (texto o mapa de bits/imagen).
        supports_styles: Indica si el formato admite estilos avanzados como
            fuentes, colores y posiciones. Por defecto es False.
    """

    codec_name: str
    library: str
    containers: tuple[str, ...]
    sub_type: SubtitleType
    supports_styles: bool = False


_SUBTITLE_FORMATS: tuple[SubtitleFormatData, ...] = (
    # --- Codecs basados en texto ---
    SubtitleFormatData(
        codec_name="srt",
        library="srt",
        containers=(".mkv", ".srt"),
        sub_type=SubtitleType.TEXT,
        supports_styles=False,
    ),
    SubtitleFormatData(
        codec_name="ass",
        library="ass",
        containers=(".mkv", ".ass", ".ssa"),
        sub_type=SubtitleType.TEXT,
        supports_styles=True,  # Soporta fuentes, colores y posiciones complejas
    ),
    SubtitleFormatData(
        codec_name="webvtt",
        library="webvtt",
        containers=(".mkv", ".webm", ".vtt"),
        sub_type=SubtitleType.TEXT,
        supports_styles=True,
    ),
    SubtitleFormatData(
        codec_name="mov_text",
        library="mov_text",
        containers=(".mp4", ".mov", ".3gp"),
        sub_type=SubtitleType.TEXT,
        supports_styles=False,  # Subtítulo de texto plano nativo de MP4
    ),
    # --- Codecs basados en imagen (solo lectura / burn-in) ---
    SubtitleFormatData(
        codec_name="dvd_subtitle",
        library="dvdsub",
        containers=(".mkv", ".vob"),
        sub_type=SubtitleType.IMAGE,
        supports_styles=False,
    ),
    SubtitleFormatData(
        codec_name="hdmv_pgs_subtitle",
        library="pgssub",
        containers=(".mkv", ".m2ts"),
        sub_type=SubtitleType.IMAGE,
        supports_styles=False,
    ),
)

SUBTITLE_FORMATS: Mapping[str, SubtitleFormatData] = MappingProxyType(
    {fmt.codec_name: fmt for fmt in _SUBTITLE_FORMATS}
)
"""dict[str, SubtitleFormatData]: Subtítulos indexados por nombre de códec."""
