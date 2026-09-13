"""Tests para el mixin de escalado (pymedia.models.mixins.scale_mixin)."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from pymedia.errors import (
    InvalidArgumentError,
    InvalidParameterError,
    MissingPropertyError,
)
from pymedia.models.media import Media, Video
from pymedia.models.mixins.scale_mixin import ScaleMixin
from pymedia.types import Dimensions, ScaleMode

_IGNORED_MSG = "Ignored scale. Target scale > video resolution, it requires upscale."


def _mixin(
    scale_mode: ScaleMode = ScaleMode.STRETCH,
    video: Video | None = None,
) -> ScaleMixin:
    """ScaleMixin sobre un vídeo 1920x1080 por defecto, en el modo indicado."""
    mixin = ScaleMixin(scale_mode=scale_mode)
    mixin.media = Media(
        path=Path("clip.mp4"),
        video=(
            video
            if video is not None
            else Video(path=Path("clip.mp4"), width=1920, height=1080)
        ),
    )
    return mixin


@pytest.fixture(autouse=True)
def _fake_translate(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fija `_` como identidad para que los mensajes no dependan del idioma."""
    monkeypatch.setattr("pymedia.models.mixins.scale_mixin._", lambda msgid: msgid)


class TestCreateScale:
    """Pruebas de `create_scale`."""

    def test_equal_dimensions_are_noop(self) -> None:
        """Comprueba que escalar a las mismas dimensiones no hace nada."""
        mixin = _mixin()
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="1920x1080")

        assert mixin.scale_to is None
        logger.warning.assert_not_called()


class TestParseErrors:
    """Pruebas de errores de parseo y validación de dimensiones."""

    @pytest.mark.parametrize("value", ["", "abc", "1280", "1280x", "x720", "12x80x720"])
    def test_invalid_dimensions_raise(self, value: str) -> None:
        """Comprueba que las dimensiones mal formadas lanzan un error."""
        mixin = _mixin()

        with pytest.raises(InvalidArgumentError) as exc_info:
            mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to=value)

        assert (
            exc_info.value.msg
            == f"\nInvalid dimensions {value}. Expected: WIDTHxHEIGHT"
        )

    @pytest.mark.parametrize("value", ["641x480", "640x481", "641x481"])
    def test_odd_dimensions_raise(self, value: str) -> None:
        """Comprueba que las dimensiones impares lanzan un error."""
        mixin = _mixin()

        with pytest.raises(InvalidParameterError) as exc_info:
            mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to=value)

        assert exc_info.value.msg == "\nTarget dimensions must be even."

    def test_video_missing_raises(self) -> None:
        """Comprueba que la ausencia de vídeo lanza un error."""
        mixin = _mixin(video=None)
        mixin.media = Media(path=Path("clip.mp4"))

        with pytest.raises(MissingPropertyError, match="video dimensions"):
            mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to="1280x720")

    def test_video_without_dimensions_raises(self) -> None:
        """Comprueba que un vídeo sin dimensiones lanza un error."""
        mixin = _mixin(video=Video(path=Path("clip.mp4")))

        with pytest.raises(MissingPropertyError, match="video dimensions"):
            mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to="1280x720")


class TestStretch:
    """Pruebas del modo de escalado STRETCH."""

    def test_downscale_keeps_target(self) -> None:
        """Comprueba que al reducir se mantiene la dimensión objetivo."""
        mixin = _mixin(scale_mode=ScaleMode.STRETCH)

        mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to="1280x720")

        assert mixin.scale_to == Dimensions(1280, 720)

    def test_upscale_rejected_without_flag(self) -> None:
        """Comprueba que ampliar sin `--upscale` se ignora con aviso."""
        mixin = _mixin(scale_mode=ScaleMode.STRETCH)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="2560x1440")

        assert mixin.scale_to is None
        logger.warning.assert_called_once_with(msg=_IGNORED_MSG)

    def test_upscale_allowed_with_flag(self) -> None:
        """Comprueba que ampliar con `--upscale` mantiene la dimensión objetivo."""
        mixin = _mixin(scale_mode=ScaleMode.STRETCH)

        mixin.create_scale(logger=Mock(), scale_upscale=True, scale_to="2560x1440")

        assert mixin.scale_to == Dimensions(2560, 1440)


class TestFit:
    """Pruebas del modo de escalado FIT."""

    @pytest.mark.parametrize(
        ("scale_to", "expected"),
        [
            ("1280x720", Dimensions(1280, 0)),
            ("1920x720", Dimensions(0, 720)),
            ("1280x640", Dimensions(0, 640)),
        ],
    )
    def test_downscale_keeps_dominant_dimension(
        self, scale_to: str, expected: Dimensions
    ) -> None:
        """Comprueba que se conserva solo la dimensión dominante."""
        mixin = _mixin(scale_mode=ScaleMode.FIT)

        mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to=scale_to)

        assert mixin.scale_to == expected

    def test_equal_dimensions_are_noop(self) -> None:
        """Comprueba que escalar a las mismas dimensiones no hace nada."""
        mixin = _mixin(scale_mode=ScaleMode.FIT)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="1920x1080")

        assert mixin.scale_to is None
        logger.warning.assert_not_called()

    def test_upscale_rejected_without_flag(self) -> None:
        """Comprueba que ampliar sin `--upscale` se ignora con aviso."""
        mixin = _mixin(scale_mode=ScaleMode.FIT)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="2560x1440")

        assert mixin.scale_to is None
        logger.warning.assert_called_once_with(msg=_IGNORED_MSG)

    def test_upscale_allowed_with_flag(self) -> None:
        """Comprueba que ampliar con `--upscale` conserva la dimensión dominante."""
        mixin = _mixin(scale_mode=ScaleMode.FIT)

        mixin.create_scale(logger=Mock(), scale_upscale=True, scale_to="2560x1440")

        assert mixin.scale_to == Dimensions(2560, 0)


class TestCover:
    """Pruebas del modo de escalado COVER."""

    @pytest.mark.parametrize(
        ("scale_to", "expected"),
        [
            ("1280x720", Dimensions(1280, 0)),
            ("1280x640", Dimensions(1280, 0)),
            ("960x720", Dimensions(0, 720)),
        ],
    )
    def test_downscale_keeps_dominant_dimension(
        self, scale_to: str, expected: Dimensions
    ) -> None:
        """Comprueba que se conserva solo la dimensión dominante."""
        mixin = _mixin(scale_mode=ScaleMode.COVER)

        mixin.create_scale(logger=Mock(), scale_upscale=False, scale_to=scale_to)

        assert mixin.scale_to == expected

    def test_equal_dimensions_are_noop(self) -> None:
        """Comprueba que escalar a las mismas dimensiones no hace nada."""
        mixin = _mixin(scale_mode=ScaleMode.COVER)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="1920x1080")

        assert mixin.scale_to is None
        logger.warning.assert_not_called()

    def test_same_width_without_flag_rejected(self) -> None:
        """Comprueba que ampliar en el mismo ancho sin flag se ignora con aviso."""
        mixin = _mixin(scale_mode=ScaleMode.COVER)
        logger = Mock()

        mixin.create_scale(logger=logger, scale_upscale=False, scale_to="1920x720")

        assert mixin.scale_to is None
        logger.warning.assert_called_once_with(msg=_IGNORED_MSG)

    def test_same_width_allowed_with_flag(self) -> None:
        """Comprueba que ampliar en el mismo ancho con flag mantiene la dimensión."""
        mixin = _mixin(scale_mode=ScaleMode.COVER)

        mixin.create_scale(logger=Mock(), scale_upscale=True, scale_to="1920x720")

        assert mixin.scale_to == Dimensions(1920, 0)


class TestToScaleCmd:
    """Pruebas de generación del filtro `scale`."""

    def test_none_returns_none(self) -> None:
        """Comprueba que sin dimensión objetivo devuelve `None`."""
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
    def test_cmd(self, width: int, height: int, expected: str) -> None:
        """Comprueba que el filtro se genera con `-2` en la dimensión libre."""
        mixin = _mixin()
        mixin.scale_to = Dimensions(width, height)

        assert mixin.to_scale_cmd() == expected
