"""Tipos de containers que soporta esta aplicación."""

SUPPORTED_ANIMATED: tuple[str, ...] = (
    ".apng",
    ".gif",
    ".webp",
)
"""tuple[str, ...]: Contenedores soportados para imágenes animadas."""

SUPPORTED_AUDIO: tuple[str, ...] = (
    ".m2ts",
    ".m4a",
    ".mka",
    ".mkv",
    ".mov",
    ".mp4",
    ".ogg",
    ".opus",
    ".ts",
    ".webm",
)
"""tuple[str, ...]: Contenedores soportados para pistas de audio."""

SUPPORTED_IMAGES: tuple[str, ...] = (
    ".jpeg",
    ".jpg",
    ".png",
    ".webp",
)
"""tuple[str, ...]: Contenedores soportados para imágenes."""

SUPPORTED_MEDIA: tuple[str, ...] = (
    ".m2ts",
    ".mkv",
    ".mov",
    ".mp4",
    ".ogg",
    ".ts",
    ".webm",
)
"""tuple[str, ...]: Contenedores soportados para vídeos con audios y subtítulos."""

SUPPORTED_SUBTITLES: tuple[str, ...] = (
    ".ass",
    ".srt",
    ".ssa",
)
"""tuple[str, ...]: Contenedores soportados para subtítulos."""
