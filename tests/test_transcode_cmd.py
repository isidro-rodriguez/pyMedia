"""Tests de transcode_cmd: comando plano y filtros correctos."""

from pathlib import Path

import pytest

from pymedia.domain.config import Config, ConflictiveJoin, Transcode
from pymedia.domain.transcoding_pipeline import TranscodingPipeline
from pymedia.ffmpeg.transcode_cmd import transcode_cmd


def _config() -> Config:
    """Crea un Config válido para tests."""
    return Config(
        transcode=Transcode(
            video_codec="libx264",
            video_preset="medium",
            video_crf=23,
            video_pix_fmt="yuv420p",
            audio_codec="aac",
            audio_bit_rate="128k",
        ),
        conflictive_join=ConflictiveJoin(
            resize_to="640",
            fps="30",
            channels="1",
            pix_fmt="yuv420p",
            confirm_transcode=True,
        ),
    )


def _pipeline(**kwargs) -> TranscodingPipeline:
    """Crea un TranscodingPipeline con parámetros opcionales."""
    return TranscodingPipeline.load(**kwargs)


def _is_flat(cmd: list) -> bool:
    """Verifica que ningún elemento del comando sea una lista anidada."""
    return all(not isinstance(arg, list) for arg in cmd)


# ─────────────────────── comando sin filtros ──────────────────


def test_cmd_no_filters_is_flat_list() -> None:
    """Sin filtros, el comando es una lista plana (sin listas anidadas)."""
    cmd = transcode_cmd(Path("video.mp4"), _config(), _pipeline())

    assert isinstance(cmd, list)
    assert _is_flat(cmd)
    assert "-filter:v" not in cmd


# ─────────────────────── comando con filtros ───────────────────


def test_cmd_with_crop_has_filter_string() -> None:
    """El crop se incluye como crop=VALORES en la cadena de filtros."""
    cmd = transcode_cmd(Path("video.mp4"), _config(), _pipeline(crop="100,100,50,50"))

    assert isinstance(cmd, list)
    assert _is_flat(cmd)
    assert "-filter:v" in cmd
    filter_idx = cmd.index("-filter:v")
    assert cmd[filter_idx + 1] == "crop=100,100,50,50"


def test_cmd_with_scale_has_filter_string() -> None:
    """El scale se incluye como scale=-2:ALTURA en la cadena de filtros."""
    cmd = transcode_cmd(Path("video.mp4"), _config(), _pipeline(scale=720))

    assert _is_flat(cmd)
    filter_idx = cmd.index("-filter:v")
    assert cmd[filter_idx + 1] == "scale=-2:720"


def test_cmd_with_crop_and_scale_joins_filters() -> None:
    """Con crop + scale, los filtros se unen con coma en un solo string."""
    cmd = transcode_cmd(
        Path("video.mp4"),
        _config(),
        _pipeline(crop="100,100,50,50", scale=720),
    )

    assert _is_flat(cmd)
    filter_idx = cmd.index("-filter:v")
    assert cmd[filter_idx + 1] == "crop=100,100,50,50,scale=-2:720"


def test_cmd_with_gyrate_90_has_transpose() -> None:
    """Gyrate=90 añade transpose=1 al filtro."""
    cmd = transcode_cmd(Path("video.mp4"), _config(), _pipeline(gyrate=90))

    assert _is_flat(cmd)
    filter_idx = cmd.index("-filter:v")
    assert "transpose=1" in cmd[filter_idx + 1]


# ─────────────────── gyrate inválido devuelve None ─────────────


@pytest.mark.parametrize("gyrate", [45, 100, 360])
def test_cmd_invalid_gyrate_returns_none(gyrate: int) -> None:
    """Un gyrate no soportado devuelve None en vez de lanzar excepción."""
    cmd = transcode_cmd(Path("video.mp4"), _config(), _pipeline(gyrate=gyrate))
    assert cmd is None
