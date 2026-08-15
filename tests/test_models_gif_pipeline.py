"""Tests para el modelo de pipeline GIF (pymedia.models.gif_pipeline)."""

from pymedia.models.gif_pipeline import GifPipeline


class TestGifPipelineDefaults:
    def test_default_values(self):
        pipeline = GifPipeline()

        assert pipeline.crop is None
        assert pipeline.end_point is None
        assert pipeline.fps is None
        assert pipeline.gyrate is None
        assert pipeline.scale is None
        assert pipeline.start_point is None

    def test_load_returns_default_pipeline(self):
        pipeline = GifPipeline.load()

        assert isinstance(pipeline, GifPipeline)
        assert pipeline.crop is None
        assert pipeline.end_point is None
        assert pipeline.fps is None
        assert pipeline.gyrate is None
        assert pipeline.scale is None
        assert pipeline.start_point is None