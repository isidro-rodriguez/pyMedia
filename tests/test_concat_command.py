"""Tests de concat_command con fixtures reales de ffmpeg."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from pymedia.commands.concat_command import concat_command
from pymedia.domain.encode_pipeline import EncodePipeline

FIXTURES = Path(__file__).parent / "fixtures"

VALID_CLIPS = ["clip_01.mp4", "clip_02.mp4", "clip_03.mp4"]
NO_AUDIO_CLIP = "clip_no_audio.mp4"


def _clip(subdir: str, name: str) -> Path:
    """Devuelve la ruta de un fixture."""
    return FIXTURES / subdir / name


def _pipeline(**kwargs) -> EncodePipeline:
    """Crea un EncodePipeline con parámetros opcionales."""
    return EncodePipeline.load(**kwargs)


# Referencia al subprocess.run real para pasar ffprobe
_real_run = subprocess.run


def _passthrough_ffprobe(cmd, *args, **kwargs):
    """Deja pasar ffprobe real, mockea ffmpeg con éxito."""
    if isinstance(cmd, list) and cmd and cmd[0] == "ffprobe":
        return _real_run(cmd, *args, **kwargs)
    return subprocess.CompletedProcess(cmd, 0, "", "")


def _count_ffmpeg_calls(mock_run) -> int:
    """Cuenta las llamadas a ffmpeg (no ffprobe)."""
    count = 0
    for call in mock_run.call_args_list:
        args = call.args
        if args and isinstance(args[0], list) and args[0] and args[0][0] == "ffmpeg":
            count += 1
    return count


# ─────────────────── mezcla con/sin audio ────────────────────


@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_concat_mixed_audio_exits_without_ffmpeg(mock_run) -> None:
    """Mezcla de vídeos con y sin audio → log error + exit, sin ffmpeg."""
    paths = [
        _clip("valid_concat", "clip_01.mp4"),
        _clip("valid_concat", NO_AUDIO_CLIP),
    ]
    with pytest.raises(SystemExit) as exc_info:
        concat_command(paths, _pipeline(), "out.mp4")
    assert exc_info.value.code == 1
    assert _count_ffmpeg_calls(mock_run) == 0


@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_concat_mixed_audio_reversed_exits(mock_run) -> None:
    """Mezcla sin/con audio (orden inverso) → también exit."""
    paths = [
        _clip("valid_concat", NO_AUDIO_CLIP),
        _clip("valid_concat", "clip_01.mp4"),
    ]
    with pytest.raises(SystemExit) as exc_info:
        concat_command(paths, _pipeline(), "out.mp4")
    assert exc_info.value.code == 1
    assert _count_ffmpeg_calls(mock_run) == 0


# ─────────────────── todos sin audio ────────────────────


@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_concat_all_without_audio(mock_run) -> None:
    """Todos sin audio → no exit, ffmpeg se ejecuta (concat a=0)."""
    paths = [
        _clip("valid_concat", NO_AUDIO_CLIP),
        _clip("valid_concat", NO_AUDIO_CLIP),
    ]
    concat_command(paths, _pipeline(), "out.mp4")
    assert _count_ffmpeg_calls(mock_run) == 1


# ─────────────────── todos con audio ────────────────────


@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_concat_all_with_audio(mock_run) -> None:
    """Todos con audio → no exit, ffmpeg se ejecuta (concat a=1)."""
    paths = [
        _clip("valid_concat", "clip_01.mp4"),
        _clip("valid_concat", "clip_02.mp4"),
    ]
    concat_command(paths, _pipeline(), "out.mp4")
    assert _count_ffmpeg_calls(mock_run) == 1