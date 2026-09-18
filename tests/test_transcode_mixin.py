"""Tests para el mixin de transcodificación (pymedia.mixins.transcode_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import MissingParameterError
from pymedia.mixins.transcode_mixin import TranscodeMixin
from pymedia.models.config import Transcode
from pymedia.utils import to_ffmpeg_value


def _transcode() -> Transcode:
    """Perfil de transcodificación de prueba."""
    return Transcode(
        video_codec="h265",
        video_preset="medium",
        video_crf=23,
        audio_codec="aac",
        audio_bit_rate="128k",
    )


def _mixin(subtitles_input: Path | None = None) -> TranscodeMixin:
    """TranscodeMixin con el fichero de subtítulos indicado."""
    return TranscodeMixin(
        subtitles_input=subtitles_input,
        transcode=_transcode(),
        transcode_video=True,
    )


class TestToBurnSubtitlesCmd:
    """Pruebas de `to_burn_subtitles_cmd`."""

    def test_builds_subtitles_filter(self) -> None:
        """Comprueba que el filtro apunta a la ruta absoluta escapada."""
        subtitle = Path("subs") / "eng_subs.srt"
        mixin = _mixin(subtitles_input=subtitle)

        assert mixin.to_burn_subtitles_cmd() == (
            f"subtitles={to_ffmpeg_value(subtitle.absolute())}"
        )

    def test_value_is_not_quoted(self) -> None:
        """Comprueba que el valor no se entrecomilla: no hay shell que las quite."""
        mixin = _mixin(subtitles_input=Path("subs") / "eng_subs.srt")

        value = mixin.to_burn_subtitles_cmd()

        assert value.startswith("subtitles=")
        assert "'" not in value
        assert '"' not in value

    def test_colon_of_the_path_is_escaped(self) -> None:
        """Comprueba que los dos puntos de la unidad Windows se escapan."""
        mixin = _mixin(subtitles_input=Path("C:/subs/eng_subs.srt"))

        assert r"C\\\:" in mixin.to_burn_subtitles_cmd()

    def test_quote_of_the_path_is_escaped(self) -> None:
        """Comprueba que una comilla del nombre se escapa en vez de entrecomillar."""
        subtitle = Path("subs") / "Joan's first bycicle.srt"
        mixin = _mixin(subtitles_input=subtitle)

        assert r"Joan\\\'s\\\ first\\\ bycicle.srt" in mixin.to_burn_subtitles_cmd()

    def test_without_subtitles_input_raises(self) -> None:
        """Comprueba que sin fichero de subtítulos se lanza un error."""
        mixin = _mixin()

        with pytest.raises(MissingParameterError):
            mixin.to_burn_subtitles_cmd()
