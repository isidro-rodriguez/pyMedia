"""Tests de encode_cmd que ejecutan ffmpeg real y verifican la salida."""

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from pymedia.domain.config import App, Config, ConflictiveJoin, Encode
from pymedia.domain.encode_pipeline import EncodePipeline
from pymedia.domain.media_input import load
from pymedia.ffmpeg.encode_cmd import encode_cmd

FIXTURES = Path(__file__).parent / "fixtures" / "valid_concat"
SRC = FIXTURES / "clip_01.mp4"  # 640x360, 3 segundos

OUTPUT_NAME = "clip_01.encoded.mp4"


def _probe_resolution(path: Path) -> tuple[int, int]:
    """Devuelve (width, height) del stream de vídeo con ffprobe."""
    r = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            "-show_streams",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    data = json.loads(r.stdout)
    for s in data.get("streams", []):
        if s.get("codec_type") == "video":
            return s["width"], s["height"]
    raise AssertionError("No se encontró stream de vídeo en la salida")


def _config() -> Config:
    """Config con preset rápido para acortar los tests."""
    return Config(
        encode=Encode(
            video_codec="libx264",
            video_preset="ultrafast",
            video_crf="23",
            video_pix_fmt="yuv420p",
            audio_codec="aac",
            audio_bit_rate="128k",
        ),
        conflictive_join=ConflictiveJoin(
            resize_to="640",
            fps="30",
            channels="1",
            pix_fmt="yuv420p",
            confirm_encode=True,
        ),
        app=App(logger_level="ERROR"),
    )


def _run_pipeline(pipeline: EncodePipeline, tmp_path: Path, monkeypatch) -> Path:
    """Copia el fixture a tmp, ejecuta ffmpeg real y devuelve la salida.

    La salida se genera en el CWD con nombre `stem.encoded.suffix`,
    así que cambiamos el CWD a tmp_path y verificamos ahí.
    """
    wk = tmp_path / SRC.name
    shutil.copy(SRC, wk)
    monkeypatch.chdir(tmp_path)

    media = load(wk)
    cmd = encode_cmd(wk, _config(), media, pipeline)
    assert cmd is not None
    subprocess.run(cmd, capture_output=True, text=True, check=True)

    out = tmp_path / OUTPUT_NAME
    assert out.exists(), f"Salida no generada: {out}"
    return out


# ──────────────── comandos reales con ffmpeg ─────────────────


def test_cmd_no_filters_real(tmp_path, monkeypatch) -> None:
    """Sin filtros, la salida conserva 640x360."""
    out = _run_pipeline(EncodePipeline(), tmp_path, monkeypatch)
    assert _probe_resolution(out) == (640, 360)


def test_cmd_with_crop_real(tmp_path, monkeypatch) -> None:
    """Crop 100,50,25,25 → salida 490x310."""
    out = _run_pipeline(EncodePipeline(crop="100,50,25,25"), tmp_path, monkeypatch)
    assert _probe_resolution(out) == (490, 310)


def test_cmd_with_scale_real(tmp_path, monkeypatch) -> None:
    """Scale 180 → salida 320x180."""
    out = _run_pipeline(EncodePipeline(scale=180), tmp_path, monkeypatch)
    assert _probe_resolution(out) == (320, 180)


def test_cmd_with_gyrate_90_real(tmp_path, monkeypatch) -> None:
    """Gyrate 90 → dimensiones intercambiadas (360x640)."""
    out = _run_pipeline(EncodePipeline(gyrate=90), tmp_path, monkeypatch)
    assert _probe_resolution(out) == (360, 640)


def test_cmd_with_gyrate_180_real(tmp_path, monkeypatch) -> None:
    """Gyrate 180 → mismas dimensiones (640x360)."""
    out = _run_pipeline(EncodePipeline(gyrate=180), tmp_path, monkeypatch)
    assert _probe_resolution(out) == (640, 360)


def test_cmd_with_gyrate_270_real(tmp_path, monkeypatch) -> None:
    """Gyrate 270 → dimensiones intercambiadas (360x640)."""
    out = _run_pipeline(EncodePipeline(gyrate=270), tmp_path, monkeypatch)
    assert _probe_resolution(out) == (360, 640)


def test_cmd_crop_and_scale_real(tmp_path, monkeypatch) -> None:
    """Crop + scale combinados producen salida de altura correcta."""
    out = _run_pipeline(
        EncodePipeline(crop="100,50,25,25", scale=180), tmp_path, monkeypatch
    )
    _, h = _probe_resolution(out)
    assert h == 180


@pytest.mark.parametrize("gyrate", [45, 100, 360])
def test_cmd_invalid_gyrate_returns_none(gyrate: int, tmp_path) -> None:
    """Un gyrate no soportado devuelve None sin ejecutar ffmpeg."""
    wk = tmp_path / SRC.name
    shutil.copy(SRC, wk)
    media = load(wk)
    cmd = encode_cmd(wk, _config(), media, EncodePipeline(gyrate=gyrate))
    assert cmd is None
