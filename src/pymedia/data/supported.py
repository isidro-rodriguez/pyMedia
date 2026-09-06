"""Tipos de `data` que soporta esta aplicación."""


class SUPPORTED:
    """Restricción de los tipos, considerados en `data`, que soporta la aplicación."""

    ANIMATED: tuple[str, ...] = (
        ".apng",
        ".gif",
        ".webp",  # TODO: pendiente de implementar
    )

    AUDIO: tuple[str, ...] = (
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

    AUDIO_CODECS: tuple[str, ...] = (
        "aac",
        "eac3",
        "opus",
    )

    IMAGES: tuple[str, ...] = (
        ".jpeg",
        ".jpg",
        ".png",
        ".webp",
    )

    LANGUAGES: tuple[str, ...] = (
        "english",
        "spanish",
        "system",
    )

    CONTAINERS: tuple[str, ...] = (
        ".m2ts",
        ".mkv",
        ".mov",
        ".mp4",
        ".ts",
        ".webm",
    )

    SUBTITLES: tuple[str, ...] = (
        ".ass",
        ".srt",
        ".ssa",
    )

    SUBTITLE_CODECS: tuple[str, ...] = (
        "ass",
        "srt",
        "ssa",
    )

    VIDEO_CODECS: tuple[str, ...] = (
        "av1",
        "h264",
        "h265",
    )
