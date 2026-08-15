"""Tests para el modelo de pipeline de vídeo (pymedia.models.video_pipeline)."""

import pytest

from pymedia.models.video_pipeline import VideoPipeline


class TestVideoPipelineDefaults:
    def test_default_values(self):
        pipeline = VideoPipeline()

        assert pipeline.crop is None
        assert pipeline.gyrate is None
        assert pipeline.remux is False
        assert pipeline.scale is None
        assert pipeline.trim_points is None

    def test_load_returns_default_pipeline(self):
        pipeline = VideoPipeline.load()

        assert isinstance(pipeline, VideoPipeline)
        assert pipeline.crop is None
        assert pipeline.gyrate is None
        assert pipeline.remux is False
        assert pipeline.scale is None
        assert pipeline.trim_points is None


class TestVideoPipelineRequiresEncode:
    def test_false_when_no_operations(self):
        pipeline = VideoPipeline()

        assert pipeline.requires_encode is False

    @pytest.mark.parametrize(
        "pipeline",
        [
            VideoPipeline(crop=["crop=1520:1080:200:0"]),
            VideoPipeline(gyrate="transpose=1"),
            VideoPipeline(remux=True),
            VideoPipeline(scale=["scale=-2:720"]),
            VideoPipeline(
                crop=["crop=1520:1080:200:0"],
                gyrate="transpose=1",
                scale=["scale=-2:720"],
            ),
        ],
    )
    def test_true_when_operation_present(self, pipeline):
        assert pipeline.requires_encode is True

    def test_trim_points_does_not_require_encode(self):
        pipeline = VideoPipeline(trim_points="10.0,20.0")

        assert pipeline.requires_encode is False