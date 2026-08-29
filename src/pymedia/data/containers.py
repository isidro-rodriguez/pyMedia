"""Listas globales de extensiones de contenedor soportadas por la aplicación."""

# =============================================================================
# Extensión genéricas de containers para validaciones de entrada
# =============================================================================

ANIMATED_IMAGE_CONTAINERS: tuple[str, ...] = (
    ".apng",
    ".avif",
    ".flif",
    ".gif",
    ".mng",
    ".webp",
)
"""tuple[str, ...]: Extensiones de contenedores para imágenes animadas."""


AUDIO_CONTAINERS: tuple[str, ...] = (
    ".aac",
    ".ac3",
    ".aif",
    ".aiff",
    ".alac",
    ".amr",
    ".ape",
    ".au",
    ".caf",
    ".dts",
    ".flac",
    ".m4a",
    ".m4b",
    ".mid",
    ".midi",
    ".mka",
    ".mp2",
    ".mp3",
    ".mpc",
    ".oga",
    ".ogg",
    ".opus",
    ".ra",
    ".shn",
    ".voc",
    ".wav",
    ".wma",
    ".wv",
)
"""tuple[str, ...]: Extensiones de contenedores para archivos de audio."""


IMAGE_CONTAINERS: tuple[str, ...] = (
    ".ai",
    ".avif",
    ".bmp",
    ".cr2",
    ".cur",
    ".dds",
    ".dng",
    ".eps",
    ".gif",
    ".heic",
    ".heif",
    ".icns",
    ".ico",
    ".iff",
    ".jfif",
    ".jpeg",
    ".jpg",
    ".nef",
    ".orf",
    ".pbm",
    ".png",
    ".pnm",
    ".ppm",
    ".psd",
    ".raw",
    ".svg",
    ".tga",
    ".tif",
    ".tiff",
    ".webp",
    ".xcf",
)
"""tuple[str, ...]: Extensiones de contenedores para imágenes estáticas o 
archivos gráficos."""


SUBTITLE_CONTAINERS: tuple[str, ...] = (
    ".aqt",
    ".ass",
    ".cap",
    ".dfxp",
    ".idx",
    ".lrc",
    ".mcc",
    ".mpl",
    ".pjs",
    ".rt",
    ".scc",
    ".smi",
    ".sami",
    ".srt",
    ".ssa",
    ".stl",
    ".sub",
    ".ttml",
    ".usf",
    ".vtt",
    ".xml",
)
"""tuple[str, ...]: Extensiones de contenedores para formatos de subtítulos 
autónomos."""


VIDEO_CONTAINERS: tuple[str, ...] = (
    ".3g2",
    ".3gp",
    ".asf",
    ".avi",
    ".bink",
    ".dvr",
    ".flv",
    ".gxf",
    ".ivf",
    ".m2ts",
    ".mkv",
    ".mj2",
    ".mov",
    ".mp4",
    ".mpeg",
    ".mpg",
    ".mts",
    ".mxf",
    ".ogv",
    ".rm",
    ".rmvb",
    ".ts",
    ".vob",
    ".webm",
    ".wmv",
    ".wtv",
)
"""tuple[str, ...]: Extensiones de contenedores para archivos de vídeo."""

# =============================================================================
#  Restricción de containers válidos para salidas de la aplicación.
# =============================================================================


OUTPUT_IMAGE_CONTAINERS: tuple[str, ...] = (
    ".jpeg",
    ".jpg",
    ".png",
    ".webp",
)
"""tuple[str, ...]: Extensiones de contenedores para imágenes de salida."""
