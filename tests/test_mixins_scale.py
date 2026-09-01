"""Tests para el mixin de escalado (pymedia.models.mixins.scale_mixin)."""

from unittest.mock import Mock

import pytest

from pymedia.data.types import Dimensions, ScaleMode
from pymedia.errors import InvalidParameterError, MissingMediaPropertyError
from pymedia.models.media import Media, Video
from pymedia.models.mixins.scale_mixin import ScaleMixin

_IGNORED_MSG = "Ignored scale. Target scale > video resolution, it requires upscale."


def _mixin(
    scale_mode: ScaleMode = ScaleMode.STRETCH,
    video: Video | None = None,
) -> ScaleMixin:
    """ScaleMixin sobre un vídeo 1920x1080 por defecto, en el modo indicado."""
    mixin = ScaleMixin(scale_mode=scale_mode)
    mixin.media = Media(
        video=video if video is not None else Video(width=1920, height=1080)
    )
    return mixin


@pytest.fixture(autouse=True)
def _fake_translate(monkeypatch):
    """Fija `_` como identidad para que los mensajes no dependan del idioma."""
    monkeypatch.setattr("pymedia.models.mixins.scale_mixin._", lambda msgid: msgid)


class TestCreateScale:
    def test_equal_dimensions_are_noop(self):
        mixin = _mixin()
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="1920x1080")

        assert mixin.scale_to is None
        logger.warning.assert_not_called()


class TestParseErrors:
    @pytest.mark.parametrize("value", ["", "abc", "1280", "1280x", "x720", "12x80x720"])
    def test_invalid_dimensions_raise(self, value):
        mixin = _mixin()

        with pytest.raises(InvalidParameterError) as exc_info:
            mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to=value)

        assert (
            exc_info.value.message
            == f"Invalid dimensions {value}. Expected: WIDTHxHEIGHT"
        )

    @pytest.mark.parametrize("value", ["641x480", "640x481", "641x481"])
    def test_odd_dimensions_raise(self, value):
        mixin = _mixin()

        with pytest.raises(InvalidParameterError) as exc_info:
            mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to=value)

        assert exc_info.value.message == "Target dimensions must be even."

    def test_video_missing_raises(self):
        mixin = _mixin(video=None)
        mixin.media = Media()

        with pytest.raises(MissingMediaPropertyError, match="video dimensions"):
            mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to="1280x720")

    def test_video_without_dimensions_raises(self):
        mixin = _mixin(video=Video())

        with pytest.raises(MissingMediaPropertyError, match="video dimensions"):
            mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to="1280x720")


class TestStretch:
    def test_downscale_keeps_target(self):
        mixin = _mixin(scale_mode=ScaleMode.STRETCH)

        mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to="1280x720")

        assert mixin.scale_to == Dimensions(1280, 720)

    def test_upscale_rejected_without_flag(self):
        mixin = _mixin(scale_mode=ScaleMode.STRETCH)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="2560x1440")

        assert mixin.scale_to is None
        logger.warning.assert_called_once_with(msg=_IGNORED_MSG)

    def test_upscale_allowed_with_flag(self):
        mixin = _mixin(scale_mode=ScaleMode.STRETCH)

        mixin.create_scale(logger=Mock(), scale_upscale=True, scale_to="2560x1440")

        assert mixin.scale_to == Dimensions(2560, 1440)


class TestFit:
    @pytest.mark.parametrize(
        ("scale_to", "expected"),
        [
            ("1280x720", Dimensions(1280, 0)),
            ("1920x720", Dimensions(0, 720)),
            ("1280x640", Dimensions(0, 640)),
        ],
    )
    def test_downscale_keeps_dominant_dimension(self, scale_to, expected):
        mixin = _mixin(scale_mode=ScaleMode.FIT)

        mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to=scale_to)

        assert mixin.scale_to == expected

    def test_equal_dimensions_are_noop(self):
        mixin = _mixin(scale_mode=ScaleMode.FIT)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="1920x1080")

        assert mixin.scale_to is None
        logger.warning.assert_not_called()

    def test_upscale_rejected_without_flag(self):
        mixin = _mixin(scale_mode=ScaleMode.FIT)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="2560x1440")

        assert mixin.scale_to is None
        logger.warning.assert_called_once_with(msg=_IGNORED_MSG)

    def test_upscale_allowed_with_flag(self):
        mixin = _mixin(scale_mode=ScaleMode.FIT)

        mixin.create_scale(logger=Mock(), scale_upscale=True, scale_to="2560x1440")

        assert mixin.scale_to == Dimensions(2560, 0)


class TestCover:
    @pytest.mark.parametrize(
        ("scale_to", "expected"),
        [
            ("1280x720", Dimensions(1280, 0)),
            ("1280x640", Dimensions(1280, 0)),
            ("960x720", Dimensions(0, 720)),
        ],
    )
    def test_downscale_keeps_dominant_dimension(self, scale_to, expected):
        mixin = _mixin(scale_mode=ScaleMode.COVER)

        mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to=scale_to)

        assert mixin.scale_to == expected

    def test_equal_dimensions_are_noop(self):
        mixin = _mixin(scale_mode=ScaleMode.COVER)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="1920x1080")

        assert mixin.scale_to is None
        logger.warning.assert_not_called()

    def test_same_width_without_flag_rejected(self):
        mixin = _mixin(scale_mode=ScaleMode.COVER)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="1920x720")

        assert mixin.scale_to is None
        logger.warning.assert_called_once_with(msg=_IGNORED_MSG)

    def test_same_width_allowed_with_flag(self):
        mixin = _mixin(scale_mode=ScaleMode.COVER)

        mixin.create_scale(logger=Mock(), scale_upscale=True, scale_to="1920x720")

        assert mixin.scale_to == Dimensions(1920, 0)


class TestToScaleCmd:
    def test_none_returns_none(self):
        mixin = _mixin()
        mixin.scale_to = None

        assert mixin.to_scale_cmd() is None

    @pytest.mark.parametrize(
        ("width", "height", "expected"),
        [
            (1280, 720, "scale=1280:720"),
            (1280, 0, "scale=1280:-2"),
            (0, 720, "scale=-2:720"),
        ],
    )
    def test_cmd(self, width, height, expected):
        mixin = _mixin()
        mixin.scale_to = Dimensions(width, height)

        assert mixin.to_scale_cmd() == expected
