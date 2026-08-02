# src/pymedia/domain/media_input.py
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path

from pymedia.ffmpeg.probe import probe as ffprobe
from pymedia.utils import parse_fraction, to_float, to_int


@dataclass(frozen=True)
class Video:
    codec: str | None = None
    width: int | None = None
    height: int | None = None
    fps: Fraction | None = None
    bit_rate: int | None = None
    pix_fmt: str | None = None
    aspect_ratio: str | None = None


@dataclass(frozen=True)
class Audio:
    codec: str | None = None
    sample_rate: int | None = None
    channels: int | None = None
    channel_layout: str | None = None
    bit_rate: int | None = None
    language: str | None = None


@dataclass(frozen=True)
class MediaInput:
    path: Path
    duration: float | None = None
    size: int | None = None
    format_name: str | None = None
    video: Video | None = None
    audio: Audio | None = None


def load(path: Path) -> MediaInput:
    """Mapea el JSON de ffprobe a MediaInput."""
    data = ffprobe(path)

    video = None
    audio = None

    for stream in data.get("streams", []):
        codec_type = stream.get("codec_type")
        tags = stream.get("tags", {})
        language = tags.get("language")

        if codec_type == "video":
            video = Video(
                codec=stream.get("codec_name"),
                width=stream.get("width"),
                height=stream.get("height"),
                fps=parse_fraction(stream.get("avg_frame_rate")),
                bit_rate=to_int(stream.get("bit_rate")),
                pix_fmt=stream.get("pix_fmt"),
                aspect_ratio=stream.get("display_aspect_ratio"),
            )
        elif codec_type == "audio":
            audio = Audio(
                codec=stream.get("codec_name"),
                sample_rate=to_int(stream.get("sample_rate")),
                channels=stream.get("channels"),
                channel_layout=stream.get("channel_layout"),
                bit_rate=to_int(stream.get("bit_rate")),
                language=language,
            )

    fmt = data.get("format", {})

    return MediaInput(
        path=path,
        duration=to_float(fmt.get("duration")),
        size=to_int(fmt.get("size")),
        format_name=fmt.get("format_name"),
        video=video,
        audio=audio,
    )
