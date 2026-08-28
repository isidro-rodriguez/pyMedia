"""Tests para el mixin de redimensionado (pymedia.models.mixins.resize_mixin)."""

from unittest.mock import Mock

import pytest

from pymedia.errors import (
    ConflictiveResizeDimensionsParametersError,
    MissingMediaPropertyError,
)
from pymedia.models.media import Media, Video
from pymedia.models.mixins.resize_mixin import ResizeMixin


def _make_mixin(video: Video | None = None) -> ResizeMixin:
    """Devuelve un ResizeMixin sobre un vídeo fuente 1920x1080 por defecto."""
    mixin = ResizeMixin()
    mixin.media = Media(
        video=video if video is not None else Video(width=1920, height=1080)
    )
    return mixin


class TestCreateResize:
    def test_width_and_height_together_raise_conflict(self):
        mixin = _make_mixin()

        with pytest.raises(ConflictiveResizeDimensionsParametersError):
            mixin.create_resize(logger=Mock(), width=1280, height=720)

    def test_without_dimensions_is_noop(self):
        mixin = _make_mixin()

        mixin.create_resize(logger=Mock())

        assert mixin.resize_width is None
        assert mixin.resize_height is None
        assert mixin.resize_upscale is False

    @pytest.mark.parametrize(
        ("kwargs", "property_name"),
        [
            ({"width": 640}, "width"),
            ({"height": 480}, "height"),
        ],
    )
    def test_raises_when_video_has_no_dimensions(self, kwargs, property_name):
        mixin = _make_mixin(video=Video())

        with pytest.raises(MissingMediaPropertyError, match=property_name):
            mixin.create_resize(logger=Mock(), **kwargs)

    def test_raises_when_video_is_missing(self):
        mixin = ResizeMixin()
        mixin.media = Media()

        with pytest.raises(MissingMediaPropertyError, match="width"):
            mixin.create_resize(logger=Mock(), width=640)

    @pytest.mark.parametrize(
        ("dimension", "target", "source", "upscale", "expected"),
        [
            # Igual a la fuente -> rechazada
            ("width", 1920, 1920, False, None),
            ("height", 1080, 1080, False, None),
            # Menor que la fuente -> aceptada sin upscale
            ("width", 1280, 1920, False, 1280),
            ("height", 720, 1080, False, 720),
            # Mayor que la fuente -> rechazada sin upscale, aceptada con upscale
            ("width", 2560, 1920, False, None),
            ("width", 2560, 1920, True, 2560),
            ("height", 2160, 1080, False, None),
            ("height", 2160, 1080, True, 2160),
        ],
    )
    def test_resize_dimension(self, dimension, target, source, upscale, expected):
        mixin = _make_mixin(video=Video(width=1920, height=1080))

        mixin.create_resize(logger=Mock(), upscale=upscale, **{dimension: target})

        attr = getattr(mixin, f"resize_{dimension}")
        other = mixin.resize_height if dimension == "width" else mixin.resize_width
        assert attr == expected
        assert other is None

    def test_equal_dimension_warns_and_rejects(self):
        mixin = _make_mixin()
        logger = Mock()

        mixin.create_resize(logger=logger, width=1920)

        assert mixin.resize_width is None
        logger.warning.assert_called_once_with(
            key="resize_rejected_equal", dimension="width"
        )

    def test_upscale_rejected_warns_and_rejects(self):
        mixin = _make_mixin()
        logger = Mock()

        mixin.create_resize(logger=logger, width=2560)

        assert mixin.resize_width is None
        logger.warning.assert_called_once_with(
            key="upscale_rejected", target=2560, source=1920
        )


class TestToResizeCmd:
    @pytest.mark.parametrize(
        ("width", "height", "upscale", "expected"),
        [
            (1280, None, False, "scale='min(1280,iw)':-2"),
            (2560, None, True, "scale=2560:-2"),
            (None, 720, False, "scale=-2:'min(720,ih)'"),
            (None, 2160, True, "scale=-2:2160"),
            (None, None, False, None),
        ],
    )
    def test_to_resize_cmd(self, width, height, upscale, expected):
        mixin = ResizeMixin()
        mixin.resize_width = width
        mixin.resize_height = height
        mixin.resize_upscale = upscale

        assert mixin.to_resize_cmd() == expected
