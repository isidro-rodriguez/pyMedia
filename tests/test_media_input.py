"""Tests de media_input.load sobre fixtures reales de ffmpeg."""

import subprocess
from fractions import Fraction
from pathlib import Path

import pytest

from pymedia.domain.media_input import Audio, MediaInput, Video, load

FIXTURES = Path(__file__).parent / "fixtures"

VALID_CONCAT_CLIPS = ["clip_01.mp4", "clip_02.mp4", "clip_03.mp4"]

# Archivos que ffprobe no puede leer → CalledProcessError
INVALID_FILES = [
    "empty.mp4",
    "not_video.mp4",
    "random_bytes.mp4",
    "corrupt_truncated.mp4",
]


def _clip(subdir: str, name: str) -> Path:
    """Devuelve la ruta de un fixture."""
    return FIXTURES / subdir / name


# ─────────────────────── clips válidos ──────────────────────


@pytest.mark.parametrize("name", VALID_CONCAT_CLIPS)
def test_load_returns_media_input(name: str) -> None:
    """load devuelve un MediaInput para clips válidos."""
    media = load(_clip("valid_concat", name))
    assert isinstance(media, MediaInput)


@pytest.mark.parametrize("name", VALID_CONCAT_CLIPS)
def test_load_video_props(name: str) -> None:
    """El vídeo mapea codec, resolución, fps y pix_fmt."""
    media = load(_clip("valid_concat", name))
    assert media.video is not None
    assert isinstance(media.video, Video)
    assert media.video.codec == "h264"
    assert media.video.width == 640
    assert media.video.height == 360
    assert media.video.fps == Fraction(30, 1)
    assert media.video.pix_fmt == "yuv420p"


@pytest.mark.parametrize("name", VALID_CONCAT_CLIPS)
def test_load_audio_props(name: str) -> None:
    """El audio mapea codec, sample_rate, channels y channel_layout."""
    media = load(_clip("valid_concat", name))
    assert media.audio is not None
    assert isinstance(media.audio, Audio)
    assert media.audio.codec == "aac"
    assert media.audio.sample_rate == 44100
    assert media.audio.channels == 1
    assert media.audio.channel_layout == "mono"


@pytest.mark.parametrize("name", VALID_CONCAT_CLIPS)
def test_load_format_props(name: str) -> None:
    """El formato mapea duration, size y format_name."""
    media = load(_clip("valid_concat", name))
    assert media.duration is not None
    assert media.duration.total_seconds() == pytest.approx(3.0, abs=0.1)
    assert media.size is not None
    assert media.size > 0
    assert media.format_name is not None
    assert "mp4" in media.format_name


@pytest.mark.parametrize("name", VALID_CONCAT_CLIPS)
def test_load_path_preserved(name: str) -> None:
    """El path del MediaInput coincide con el pasado a load."""
    path = _clip("valid_concat", name)
    media = load(path)
    assert media.path == path


# ─────────────────────── audio only ─────────────────────────


def test_load_audio_only_no_video() -> None:
    """audio_only.mp4 no tiene stream de vídeo."""
    media = load(_clip("invalid", "audio_only.mp4"))
    assert media.video is None
    assert media.audio is not None
    assert media.audio.codec == "aac"


# ─────────────────────── clips inválidos ────────────────────


@pytest.mark.parametrize("name", INVALID_FILES)
def test_load_invalid_raises(name: str) -> None:
    """Los archivos inválidos lanzan CalledProcessError."""
    with pytest.raises(subprocess.CalledProcessError):
        load(_clip("invalid", name))


def test_load_nonexistent_raises() -> None:
    """Un path inexistente lanza CalledProcessError."""
    with pytest.raises(subprocess.CalledProcessError):
        load(Path("no_existe.mp4"))