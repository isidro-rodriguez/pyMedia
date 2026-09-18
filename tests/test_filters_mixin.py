"""Tests para el mixin de filtros (pymedia.mixins.filters_mixin)."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from pymedia.commands.frames.parameters import FramesParameters
from pymedia.mixins.filters_mixin import FiltersMixin
from pymedia.models.media import Media, Video
from pymedia.types import OverwriteMode, RotateMode, ScaleMode


def _mixin(video: Video | None = None) -> FiltersMixin:
    """Devuelve un FiltersMixin STRETCH sobre un vídeo 1920x1080 por defecto."""
    mixin = FiltersMixin(scale_mode=ScaleMode.STRETCH)
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
    monkeypatch.setattr("pymedia.mixins.scale_mixin._", lambda msgid: msgid)


class TestCreateFilters:
    """Pruebas de `create_filters`."""

    def test_without_options_is_noop(self) -> None:
        """Comprueba que sin opciones no se crea ningún filtro."""
        mixin = _mixin()

        mixin.create_filters(logger=Mock())

        assert mixin.crop_area is None
        assert mixin.scale_to is None
        assert mixin.rotate is None
        assert mixin.hflip is False
        assert mixin.vflip is False

    def test_crop(self) -> None:
        """Comprueba que se crea el área de recorte."""
        mixin = _mixin()

        mixin.create_filters(logger=Mock(), crop="100,100,10,10")

        assert mixin.crop_area == (100, 100, 10, 10)

    def test_scale(self) -> None:
        """Comprueba que se crea la dimensión de escalado."""
        mixin = _mixin()

        mixin.create_filters(logger=Mock(), scale_to="1280x720")

        assert mixin.scale_to == (1280, 720)

    def test_rotate(self) -> None:
        """Comprueba que se crea el ángulo de rotación."""
        mixin = _mixin()

        mixin.create_filters(logger=Mock(), rotate=RotateMode.D90)

        assert mixin.rotate is RotateMode.D90

    def test_flip(self) -> None:
        """Comprueba que se crean los volteos horizontal y vertical."""
        mixin = _mixin()

        mixin.create_filters(logger=Mock(), hflip=True, vflip=True)

        assert mixin.hflip is True
        assert mixin.vflip is True

    def test_scale_mode_default_is_preserved(self) -> None:
        """Comprueba que `scale_mode=None` conserva el valor actual."""
        mixin = _mixin()
        mixin.scale_mode = ScaleMode.FIT

        mixin.create_filters(logger=Mock(), scale_to="1280x720")

        assert mixin.scale_mode is ScaleMode.FIT

    def test_scale_mode_is_overridden(self) -> None:
        """Comprueba que se sobreescribe el modo de escalado si se indica."""
        mixin = _mixin()

        mixin.create_filters(
            logger=Mock(),
            scale_to="1280x720",
            scale_mode=ScaleMode.COVER,
        )

        assert mixin.scale_mode is ScaleMode.COVER


class TestToFiltersCmd:
    """Pruebas de `to_filters_cmd`."""

    def test_without_filters_returns_empty_string(self) -> None:
        """Comprueba que sin filtros se devuelve una cadena vacía."""
        mixin = _mixin()

        assert mixin.to_filters_cmd() == ""

    def test_crop_only(self) -> None:
        """Comprueba que solo el recorte produce el filtro crop."""
        mixin = _mixin()
        mixin.create_filters(logger=Mock(), crop="100,100,10,10")

        assert mixin.to_filters_cmd() == "crop=100:100:10:10"

    def test_scale_only(self) -> None:
        """Comprueba que solo el escalado produce el filtro scale."""
        mixin = _mixin()
        mixin.create_filters(logger=Mock(), scale_to="1280x720")

        assert mixin.to_filters_cmd() == "scale=1280:720"

    def test_hflip_only(self) -> None:
        """Comprueba que solo el volteo horizontal produce el filtro hflip."""
        mixin = _mixin()
        mixin.create_filters(logger=Mock(), hflip=True)

        assert mixin.to_filters_cmd() == "hflip"

    def test_vflip_only(self) -> None:
        """Comprueba que solo el volteo vertical produce el filtro vflip."""
        mixin = _mixin()
        mixin.create_filters(logger=Mock(), vflip=True)

        assert mixin.to_filters_cmd() == "vflip"

    def test_flip_both(self) -> None:
        """Comprueba que ambos volteos se concatenan separados por coma."""
        mixin = _mixin()
        mixin.create_filters(logger=Mock(), hflip=True, vflip=True)

        assert mixin.to_filters_cmd() == "hflip,vflip"

    def test_rotate_only(self) -> None:
        """Comprueba que solo la rotación produce el filtro transpose."""
        mixin = _mixin()
        mixin.create_filters(logger=Mock(), rotate=RotateMode.D180)

        assert mixin.to_filters_cmd() == "transpose=1,transpose=1"

    def test_all_filters_in_order(self) -> None:
        """Comprueba el orden crop, scale, flip, rotate en la cadena final."""
        mixin = _mixin()
        mixin.create_filters(
            logger=Mock(),
            crop="100,100,10,10",
            scale_to="1280x720",
            hflip=True,
            vflip=True,
            rotate=RotateMode.D90,
        )

        expected = "crop=100:100:10:10,scale=1280:720,hflip,vflip,transpose=1"
        assert mixin.to_filters_cmd() == expected

    def test_rejected_scale_is_omitted(self) -> None:
        """Comprueba que un escalado rechazado no genera filtro."""
        mixin = _mixin()
        mixin.create_filters(logger=Mock(), scale_to="1920x1080")

        assert mixin.scale_to is None
        assert mixin.to_filters_cmd() == ""


class TestFiltersIntegration:
    """Prueba de integración de `create_filters` en parámetros reales."""

    def test_frames_parameters(self) -> None:
        """Comprueba la creación de filtros sobre `FramesParameters`."""
        params = FramesParameters(overwrite=OverwriteMode.NO)
        params.media = Media(
            path=Path("clip.mp4"),
            video=Video(path=Path("clip.mp4"), width=1920, height=1080),
        )

        params.create_filters(
            logger=Mock(),
            crop="100,100,10,10",
            scale_to="1280x720",
            scale_mode=ScaleMode.STRETCH,
            hflip=True,
            vflip=True,
            rotate=RotateMode.D90,
        )

        expected = "crop=100:100:10:10,scale=1280:720,hflip,vflip,transpose=1"
        assert params.to_filters_cmd() == expected
