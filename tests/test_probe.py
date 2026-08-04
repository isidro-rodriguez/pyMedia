"""Tests de probe sobre fixtures reales de ffmpeg."""

import subprocess
from pathlib import Path

import pytest

from pymedia.ffmpeg.probe import probe

FIXTURES = Path(__file__).parent / "fixtures"

VALID_CONCAT_CLIPS = ["clip_01.mp4", "clip_02.mp4", "clip_03.mp4"]
VALID_ENCODE_CLIPS = [f"clip_{i:02d}.mp4" for i in range(4, 10)]

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
def test_probe_returns_dict(name: str) -> None:
    """Cada clip válido devuelve un dict con streams y format."""
    data = probe(_clip("valid_concat", name))
    assert isinstance(data, dict)
    assert "streams" in data
    assert "format" in data


@pytest.mark.parametrize("name", VALID_CONCAT_CLIPS)
def test_probe_valid_concat_has_two_streams(name: str) -> None:
    """Cada clip de valid_concat tiene 2 streams: vídeo + audio."""
    data = probe(_clip("valid_concat", name))
    streams = data["streams"]
    assert len(streams) == 2
    types = {s["codec_type"] for s in streams}
    assert types == {"video", "audio"}


@pytest.mark.parametrize("name", VALID_CONCAT_CLIPS)
def test_probe_valid_concat_video_props(name: str) -> None:
    """Los clips de valid_concat tienen vídeo h264, 640x360, 30 fps."""
    data = probe(_clip("valid_concat", name))
    video = next(s for s in data["streams"] if s["codec_type"] == "video")
    assert video["codec_name"] == "h264"
    assert video["width"] == 640
    assert video["height"] == 360
    assert video["avg_frame_rate"] == "30/1"


@pytest.mark.parametrize("name", VALID_CONCAT_CLIPS)
def test_probe_valid_concat_audio_props(name: str) -> None:
    """Los clips de valid_concat tienen audio aac, 44100Hz, mono."""
    data = probe(_clip("valid_concat", name))
    audio = next(s for s in data["streams"] if s["codec_type"] == "audio")
    assert audio["codec_name"] == "aac"
    assert audio["sample_rate"] == "44100"
    assert audio["channels"] == 1
    assert audio["channel_layout"] == "mono"


@pytest.mark.parametrize("name", VALID_ENCODE_CLIPS)
def test_probe_valid_encode_returns_dict(name: str) -> None:
    """Cada clip de valid_encode devuelve un dict válido."""
    data = probe(_clip("valid_encode", name))
    assert isinstance(data, dict)
    assert "streams" in data
    assert "format" in data


# ─────────────────────── audio only ─────────────────────────


def test_probe_audio_only_has_one_stream() -> None:
    """audio_only.mp4 tiene 1 solo stream de audio, sin vídeo."""
    data = probe(_clip("invalid", "audio_only.mp4"))
    streams = data["streams"]
    assert len(streams) == 1
    assert streams[0]["codec_type"] == "audio"


# ─────────────────────── clips inválidos ────────────────────


@pytest.mark.parametrize("name", INVALID_FILES)
def test_probe_invalid_raises(name: str) -> None:
    """Los archivos inválidos lanzan CalledProcessError."""
    with pytest.raises(subprocess.CalledProcessError):
        probe(_clip("invalid", name))


def test_probe_nonexistent_raises() -> None:
    """Un path inexistente lanza CalledProcessError."""
    with pytest.raises(subprocess.CalledProcessError):
        probe(Path("no_existe.mp4"))
