from dataclasses import dataclass
from enum import Enum


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
        name: Nombre identificador del códec o formato (p. ej., 'subrip',
            'ass').
        library: Nombre de la librería o códec utilizado por FFmpeg (p. ej.,
            'srt', 'mov_text').
        containers: Tupla con las extensiones de contenedor soportadas (p.
            ej., ('.mkv', '.srt')).
        sub_type: Tipo de subtítulo (texto o mapa de bits/imagen).
        supports_styles: Indica si el formato admite estilos avanzados como
            fuentes, colores y posiciones. Por defecto es False.
    """

    name: str
    library: str
    containers: tuple[str, ...]
    sub_type: SubtitleType
    supports_styles: bool = False


SUBTITLE_FORMATS = {
    # --- Codecs basados en Texto ---
    "srt": SubtitleFormatData(
        name="srt",
        library="srt",
        containers=(".mkv", ".srt"),
        sub_type=SubtitleType.TEXT,
        supports_styles=False,
    ),
    "ass": SubtitleFormatData(
        name="ass",
        library="ass",
        containers=(".mkv", ".ass", ".ssa"),
        sub_type=SubtitleType.TEXT,
        supports_styles=True,  # Soporta fuentes, colores y posiciones complejas
    ),
    "webvtt": SubtitleFormatData(
        name="webvtt",
        library="webvtt",
        containers=(".mkv", ".webm", ".vtt"),
        sub_type=SubtitleType.TEXT,
        supports_styles=True,
    ),
    "mov_text": SubtitleFormatData(
        name="mov_text",
        library="mov_text",
        containers=(".mp4", ".mov", ".3gp"),
        sub_type=SubtitleType.TEXT,
        supports_styles=False,  # Subtítulo de texto plano nativo de MP4
    ),
    # --- Codecs basados en Imagen (Solo lectura / Burn-in) ---
    "dvd_subtitle": SubtitleFormatData(
        name="dvd_subtitle",
        library="dvdsub",
        containers=(".mkv", ".vob"),
        sub_type=SubtitleType.IMAGE,
        supports_styles=False,
    ),
    "hdmv_pgs_subtitle": SubtitleFormatData(
        name="hdmv_pgs_subtitle",
        library="pgssub",
        containers=(".mkv", ".m2ts"),
        sub_type=SubtitleType.IMAGE,
        supports_styles=False,
    ),
}
