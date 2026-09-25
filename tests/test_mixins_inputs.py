"""Tests para los mixins de entrada (pymedia.mixins.media_mixin)."""

import logging
from pathlib import Path
from typing import Any

import pytest

from pymedia.errors import MissingParameterError
from pymedia.logger import Logger
from pymedia.mixins.media_mixin import MediaInputMixin, MediaListMixin
from pymedia.models.audio import get_audio_metadata
from pymedia.models.media import Media
from pymedia.models.subtitles import get_subtitles_metadata


def _logger() -> Logger:
    """Logger de prueba aislado, sin handlers de consola ni fichero."""
    return Logger(logging.getLogger("pymedia.tests"))


_EMPTY_METADATA: dict[str, Any] = {"streams": [], "format": {}}


@pytest.fixture(autouse=True)
def _fake_probe(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita ejecutar ffprobe en todos los tests de este módulo."""
    monkeypatch.setattr(
        "pymedia.ffprobe._run_ffprobe",
        lambda args, path: _EMPTY_METADATA,
    )


def _media(path: Path) -> Media:
    """Media con la ruta indicada y sin metadatos."""
    return Media(path=path)


class TestInputSingleCreate:
    """Pruebas de creación de la entrada individual."""

    def test_sets_media_with_absolute_path(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que se guardan la ruta absoluta y los metadatos."""
        monkeypatch.chdir(tmp_path)
        mixin = MediaInputMixin()
        source = Path("clip.mp4")

        mixin.create_media_input(media_input=source, logger=_logger())

        assert mixin.media == _media(source.absolute())


class TestInputSingleCmd:
    """Pruebas de generación del comando de entrada individual."""

    def test_to_media_input_cmd(self) -> None:
        """Comprueba que se genera el argumento `-i` correctamente."""
        source = Path("clip.mp4")
        mixin = MediaInputMixin(media=_media(source))

        assert mixin.to_media_input_cmd() == ["-i", str(source)]

    def test_to_media_input_cmd_missing_parameter(self) -> None:
        """Comprueba que falta lanzar un error si no hay media."""
        mixin = MediaInputMixin()

        with pytest.raises(MissingParameterError, match="media"):
            mixin.to_media_input_cmd()


class TestInputListCreate:
    """Pruebas de creación de la lista de entradas."""

    def test_creates_media_list(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que se guardan rutas absolutas y sus metadatos."""
        monkeypatch.chdir(tmp_path)
        mixin = MediaListMixin()
        source_a = Path("a.mp4")
        source_b = Path("b.mp4")

        mixin.create_media_list(media_input_list=[source_a, source_b], logger=_logger())

        assert mixin.media_list == [
            Media(path=source_a.absolute()),
            Media(path=source_b.absolute()),
        ]

    def test_load_failure_raises_missing_media(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que un fallo de ffprobe lanza un error."""
        import subprocess

        def _failing_probe(args: list[str], path: Path) -> None:
            raise subprocess.CalledProcessError(1, ["ffprobe"])

        monkeypatch.setattr("pymedia.ffprobe._run_ffprobe", _failing_probe)
        mixin = MediaListMixin()

        with pytest.raises(subprocess.CalledProcessError):
            mixin.create_media_list(media_input_list=[Path("x.mp4")], logger=_logger())


class TestInputListCmd:
    """Pruebas de generación del comando de lista de entradas."""

    def test_to_media_input_list_cmd(self) -> None:
        """Comprueba que se genera un `-i` por cada entrada."""
        mixin = MediaListMixin(
            media_list=[Media(path=Path("a.mp4")), Media(path=Path("b.mp4"))]
        )

        assert mixin.to_media_input_list_cmd() == ["-i", "a.mp4", "-i", "b.mp4"]


_SUBTITLE_METADATA = {
    "streams": [
        {
            "index": 0,
            "codec_name": "h264",
            "codec_type": "video",
            "width": 1280,
            "height": 720,
            "avg_frame_rate": "25/1",
        },
        {
            "index": 1,
            "codec_name": "aac",
            "codec_type": "audio",
            "tags": {"language": "eng"},
        },
        {
            "index": 2,
            "codec_name": "subrip",
            "codec_type": "subtitle",
            "tags": {"language": "spa", "title": "Español"},
            "disposition": {"default": 1, "forced": 0, "hearing_impaired": 0},
        },
        {
            "index": 3,
            "codec_name": "hdmv_pgs_subtitle",
            "codec_type": "subtitle",
            "tags": {"language": "ita"},
            "disposition": {"default": 0, "forced": 1},
        },
    ],
    "format": {"duration": "10.0", "size": "1024"},
}


class TestSubtitlesStreamParsing:
    """Regresión: ffprobe reporta `codec_type == "subtitle"` en singular."""

    def _media_with_streams(self, tmp_path: Path) -> Media:
        """Media parseado con metadatos ffprobe simulados."""
        mixin = MediaInputMixin()
        source = tmp_path / "clip.mkv"

        mixin.create_media_input(media_input=source, logger=_logger())

        media = mixin.media
        assert media is not None
        return media

    def test_populates_subtitles_streams(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que las pistas `subtitle` se parsean y se indexan."""
        monkeypatch.setattr(
            "pymedia.ffprobe._run_ffprobe",
            lambda args, path: _SUBTITLE_METADATA,
        )
        media = self._media_with_streams(tmp_path)

        assert media.subtitles is not None
        assert len(media.subtitles) == 2
        first, second = media.subtitles

        assert first.global_index == 2
        assert first.track_index == 0
        assert first.codec == "subrip"
        assert get_subtitles_metadata(first).language == "spa"
        assert get_subtitles_metadata(first).title == "Español"
        assert get_subtitles_metadata(first).default is True
        assert get_subtitles_metadata(first).forced is False

        assert second.global_index == 3
        assert second.track_index == 1
        assert second.codec == "hdmv_pgs_subtitle"
        assert get_subtitles_metadata(second).language == "ita"
        assert get_subtitles_metadata(second).forced is True

    def test_video_and_audio_coexist_with_subtitles(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que video/audio siguen indexándose en presencia de subtítulos."""
        monkeypatch.setattr(
            "pymedia.ffprobe._run_ffprobe",
            lambda args, path: _SUBTITLE_METADATA,
        )
        media = self._media_with_streams(tmp_path)

        assert media.video is not None
        assert media.audio is not None

        assert media.video.global_index == 0
        assert media.video.track_index == 0
        assert len(media.audio) == 1
        assert media.audio[0].global_index == 1
        assert media.audio[0].track_index == 0
        assert get_audio_metadata(media.audio[0]).language == "eng"

    def test_singular_codec_type_is_required(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Comprueba que `subtitles` (plural) no se parsea: ffprobe usa `subtitle`."""
        metadata = {
            "streams": [
                {"index": 0, "codec_name": "subrip", "codec_type": "subtitles"}
            ],
            "format": {},
        }
        monkeypatch.setattr(
            "pymedia.ffprobe._run_ffprobe",
            lambda args, path: metadata,
        )
        media = self._media_with_streams(tmp_path)

        assert media.subtitles is None

    def test_to_media_input_list_cmd_missing_parameter(self) -> None:
        """Comprueba que falta lanzar un error si no hay lista."""
        mixin = MediaListMixin()

        with pytest.raises(MissingParameterError, match="media_list"):
            mixin.to_media_input_list_cmd()
