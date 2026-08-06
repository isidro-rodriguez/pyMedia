"""Tests unitarios de EncodePipeline.validate()."""

from datetime import timedelta
from pathlib import Path

import pytest

from pymedia.models.errors import (
    InvalidCropFormatError,
    InvalidScaleError,
    NoVideoStreamError,
)
from pymedia.models.media import Media, Video
from pymedia.models.pipeline import Pipeline


def _media(video: Video | None = None) -> Media:
    """Crea un MediaInput de prueba."""
    return Media(
        path=Path("video.mp4"),
        duration=timedelta(seconds=10),
        video=video,
    )


def _video(width: int = 640, height: int = 360) -> Video:
    """Crea un Video de prueba."""
    return Video(width=width, height=height)


# ─────────────────────── crop válido ──────────────────────────


def test_validate_crop_valid_no_error() -> None:
    """Un crop válido no lanza excepción."""
    pipeline = Pipeline(crop="100,50,25,25")
    pipeline.validate(_media(_video()))
    assert pipeline.crop == "100,50,25,25"


# ─────────────────── crop sin stream de vídeo ────────────────


def test_validate_crop_no_video_ignored() -> None:
    """Sin stream de vídeo, el crop se ignora (crop = None)."""
    pipeline = Pipeline(crop="100,50,25,25")
    pipeline.validate(_media(video=None))
    assert pipeline.crop is None


# ─────────────────── crop formato inválido ───────────────────


def test_validate_crop_invalid_format_raises() -> None:
    """Formato de crop inválido lanza InvalidCropFormatError."""
    pipeline = Pipeline(crop="abc")
    with pytest.raises(InvalidCropFormatError):
        pipeline.validate(_media(_video()))


# ─────────────────── crop excede resolución ──────────────────


def test_validate_crop_exceeds_width_ignored() -> None:
    """Crop que excede el ancho se ignora (crop = None)."""
    pipeline = Pipeline(crop="400,400,0,0")
    pipeline.validate(_media(_video(width=640, height=360)))
    assert pipeline.crop is None


def test_validate_crop_exceeds_height_ignored() -> None:
    """Crop que excede el alto se ignora (crop = None)."""
    pipeline = Pipeline(crop="0,0,200,200")
    pipeline.validate(_media(_video(width=640, height=360)))
    assert pipeline.crop is None


# ─────────────────────── scale sin stream ────────────────────


def test_validate_scale_no_video_raises() -> None:
    """Sin stream de vídeo, scale lanza NoVideoStreamError."""
    pipeline = Pipeline(scale=180)
    with pytest.raises(NoVideoStreamError):
        pipeline.validate(_media(video=None))


# ─────────────────────── scale sin altura ────────────────────


def test_validate_scale_no_height_raises() -> None:
    """Sin altura disponible, scale lanza InvalidScaleError."""
    pipeline = Pipeline(scale=180)
    with pytest.raises(InvalidScaleError):
        pipeline.validate(_media(_video(height=None)))


# ─────────────────────── scale >= height ─────────────────────


def test_validate_scale_equal_height_ignored() -> None:
    """Scale == height se ignora (scale = None)."""
    pipeline = Pipeline(scale=360)
    pipeline.validate(_media(_video(height=360)))
    assert pipeline.scale is None


def test_validate_scale_greater_height_ignored() -> None:
    """Scale > height se ignora (scale = None)."""
    pipeline = Pipeline(scale=720)
    pipeline.validate(_media(_video(height=360)))
    assert pipeline.scale is None


# ─────────────────────── scale válido ────────────────────────


def test_validate_scale_valid_no_error() -> None:
    """Un scale válido no lanza excepción."""
    pipeline = Pipeline(scale=180)
    pipeline.validate(_media(_video(height=360)))
    assert pipeline.scale == 180
