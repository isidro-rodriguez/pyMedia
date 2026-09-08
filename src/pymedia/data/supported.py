"""Tipos de `data` que soporta esta aplicación."""


class SUPPORTED:
    """Restricción de los tipos, considerados en `data`, que soporta la aplicación."""

    ANIMATED: tuple[str, ...] = (
        ".apng",
        ".gif",
        ".webp",  # TODO: pendiente de implementar
    )

    AUDIO: tuple[str, ...] = (
        ".m4a",
        ".mka",
        ".ogg",
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
        ".mkv",
        ".mp4",
        ".webm",
    )

    SUBTITLES: tuple[str, ...] = (
        ".ass",
        ".srt",
        ".ssa",
    )

    SUBTITLES_CODECS: tuple[str, ...] = (
        "ass",
        "srt",
        "ssa",
    )

    VIDEO_CODECS: tuple[str, ...] = (
        "av1",
        "h264",
        "h265",
    )
