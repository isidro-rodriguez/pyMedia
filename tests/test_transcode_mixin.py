"""Tests para el mixin de transcodificación (pymedia.mixins.transcode_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import MissingParameterError
from pymedia.mixins.transcode_mixin import TranscodeMixin
from pymedia.models.config import Transcode
from pymedia.models.media import Media
from pymedia.models.subtitles import Subtitles, SubtitlesFormat
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


def _subs(codec: str, index: int, text: bool | None = None) -> Subtitles:
    """Pista de subtítulos con el códec indicado."""
    return Subtitles(
        path=Path("in.mkv"),
        track_index=index,
        format=SubtitlesFormat(codec=codec, is_text_based=text),
    )


def _mixin_with_subs(*tracks: Subtitles, convert: bool = True) -> TranscodeMixin:
    """TranscodeMixin sobre un MKV con las pistas de subtítulos dadas."""
    mixin = _mixin()
    mixin.media = Media(path=Path("in.mkv"), subtitles=list(tracks))
    mixin.convert_subtitles = convert
    return mixin


class TestSubtitlesCompatibility:
    """Pruebas de la compatibilidad de subtítulos con el contenedor de salida."""

    def test_srt_into_mkv_is_copied(self) -> None:
        """SubRip cabe en MKV y se copia sin conversión."""
        mixin = _mixin_with_subs(_subs("subrip", 0))

        assert mixin.incompatible_subtitles(container=".mkv") == []
        assert mixin.to_subtitles_copy_cmd(container=".mkv") == [
            "-map",
            "0:s:0",
            "-c:s:0",
            "copy",
        ]

    def test_text_into_mp4_is_converted_to_mov_text(self) -> None:
        """Regresión: MKV con SRT a MP4 convertía según la entrada y fallaba."""
        mixin = _mixin_with_subs(_subs("subrip", 0), _subs("ass", 1))

        assert len(mixin.incompatible_subtitles(container=".mp4")) == 2
        assert mixin.to_subtitles_copy_cmd(container=".mp4") == [
            *("-map", "0:s:0", "-c:s:0", "mov_text"),
            *("-map", "0:s:1", "-c:s:1", "mov_text"),
        ]

    def test_declined_conversion_discards_text_tracks(self) -> None:
        """Si el usuario rechaza convertir, las pistas incompatibles se omiten."""
        mixin = _mixin_with_subs(_subs("subrip", 0), convert=False)

        assert mixin.to_subtitles_copy_cmd(container=".mp4") == []

    def test_graphic_into_mp4_is_discarded(self) -> None:
        """PGS no se puede convertir a texto y se descarta; el resto se conserva."""
        mixin = _mixin_with_subs(
            _subs("hdmv_pgs_subtitle", 0, text=False), _subs("mov_text", 1)
        )

        assert mixin.to_subtitles_copy_cmd(container=".mp4") == [
            *("-map", "0:s:1", "-c:s:0", "copy"),
        ]

    def test_mov_text_into_mkv_is_converted_to_srt(self) -> None:
        """mov_text no cabe en MKV y se convierte a SubRip."""
        mixin = _mixin_with_subs(_subs("mov_text", 0))

        assert mixin.to_subtitles_copy_cmd(container=".mkv")[-1] == "srt"
