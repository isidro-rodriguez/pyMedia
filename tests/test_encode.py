"""Tests de encode con fixtures reales de ffmpeg."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from pymedia.commands.encode_command import encode_command
from pymedia.models.video_pipeline import VideoPipeline

FIXTURES = Path(__file__).parent / "fixtures"

VALID_CLIPS = ["clip_01.mp4", "clip_02.mp4", "clip_03.mp4"]
INVALID_FILES = [
    "empty.mp4",
    "not_video.mp4",
    "random_bytes.mp4",
    "corrupt_truncated.mp4",
]


def _clip(subdir: str, name: str) -> Path:
    """Devuelve la ruta de un fixture."""
    return FIXTURES / subdir / name


def _pipeline(**kwargs) -> VideoPipeline:
    """Crea un EncodePipeline con parámetros opcionales."""
    return VideoPipeline.load(**kwargs)


# Referencia al subprocess.run real para pasar ffprobe
_real_run = subprocess.run


def _passthrough_ffprobe(cmd, *args, **kwargs):
    """Deja pasar ffprobe real, mockea ffmpeg con éxito."""
    if isinstance(cmd, list) and cmd and cmd[0] == "ffprobe":
        return _real_run(cmd, *args, **kwargs)
    return subprocess.CompletedProcess(cmd, 0, "", "")


def _ffmpeg_fails(cmd, *args, **kwargs):
    """Deja pasar ffprobe real, simula error de ffmpeg."""
    if isinstance(cmd, list) and cmd and cmd[0] == "ffprobe":
        return _real_run(cmd, *args, **kwargs)
    raise subprocess.CalledProcessError(1, cmd, "", "Error simulado de ffmpeg")


def _count_ffmpeg_calls(mock_run) -> int:
    """Cuenta las llamadas a ffmpeg (no ffprobe)."""
    count = 0
    for call in mock_run.call_args_list:
        args = call.args
        if args and isinstance(args[0], list) and args[0] and args[0][0] == "ffmpeg":
            count += 1
    return count


# ─────────────────────── archivo válido ──────────────────────


@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_encode_valid_file_calls_ffmpeg(mock_run) -> None:
    """Un archivo válido dispara ffmpeg."""
    encode_command([_clip("valid_concat", "clip_01.mp4")], _pipeline(remux=True))
    assert _count_ffmpeg_calls(mock_run) == 1


# ─────────────────────── pipeline sin operaciones ─────────────


@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_encode_pipeline_without_operations_skipped(mock_run) -> None:
    """Un pipeline sin operaciones aplicables no dispara ffmpeg."""
    encode_command([_clip("valid_concat", "clip_01.mp4")], _pipeline())
    assert _count_ffmpeg_calls(mock_run) == 0


# ─────────────────────── archivos inválidos ──────────────────


@pytest.mark.parametrize("name", INVALID_FILES)
@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_encode_invalid_file_skipped(mock_run, name: str) -> None:
    """Un archivo inválido no dispara ffmpeg."""
    encode_command([_clip("invalid", name)], _pipeline(remux=True))
    assert _count_ffmpeg_calls(mock_run) == 0


# ─────────────────── mezcla válido + inválido ────────────────


@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_encode_mixed_valid_invalid(mock_run) -> None:
    """Procesa solo los válidos de una lista mixta."""
    paths = [
        _clip("valid_concat", "clip_01.mp4"),
        _clip("invalid", "empty.mp4"),
        _clip("valid_concat", "clip_02.mp4"),
    ]
    encode_command(paths, _pipeline(remux=True))
    assert _count_ffmpeg_calls(mock_run) == 2


# ─────────────────── validación fallida ──────────────────────


@patch("subprocess.run", side_effect=_passthrough_ffprobe)
def test_encode_validation_failure_skipped(mock_run) -> None:
    """Un crop mayor que la resolución salta el archivo."""
    # Los clips de valid_concat son 640x360
    pipeline = _pipeline(crop="400,400,400,400")
    encode_command([_clip("valid_concat", "clip_01.mp4")], pipeline)
    assert _count_ffmpeg_calls(mock_run) == 0


# ─────────────── error de ffmpeg no detiene bucle ─────────────


@patch("subprocess.run", side_effect=_ffmpeg_fails)
def test_encode_ffmpeg_error_continues(mock_run) -> None:
    """Un error de ffmpeg no detiene el procesamiento del siguiente archivo."""
    paths = [
        _clip("valid_concat", "clip_01.mp4"),
        _clip("valid_concat", "clip_02.mp4"),
    ]
    encode_command(paths, _pipeline(remux=True))
    # Ambos archivos intentaron ffmpeg (el error no detiene el bucle)
    assert _count_ffmpeg_calls(mock_run) == 2
