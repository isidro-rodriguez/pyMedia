"""Tests para los mixins de remultiplexado (pymedia.mixins.remux_mixin)."""

from pathlib import Path

from pymedia.mixins.remux_mixin import SortTracksMixin
from pymedia.models.audio import Audio
from pymedia.models.media import Media
from pymedia.models.subtitles import Subtitles
from pymedia.models.video import Video


def _mixin(
    media: Media,
    sort_tracks: bool = True,
) -> SortTracksMixin:
    """SortTracksMixin con la media indicada y la ordenación activada."""
    mixin = SortTracksMixin(sort_tracks=sort_tracks)
    mixin.media = media
    return mixin


def _media(
    video: Video | None = None,
    audio: list[Audio] | None = None,
    subtitles: list[Subtitles] | None = None,
) -> Media:
    """Media con los streams indicados y una ruta fija."""
    return Media(path=Path("clip.mkv"), video=video, audio=audio, subtitles=subtitles)


def _audio(language: str | None, track_index: int) -> Audio:
    """Pista de audio con idioma e índice de pista dados."""
    return Audio(path=Path("clip.mkv"), language=language, track_index=track_index)


def _subtitle(language: str | None, track_index: int) -> Subtitles:
    """Pista de subtítulos con idioma e índice de pista dados."""
    return Subtitles(path=Path("clip.mkv"), language=language, track_index=track_index)


class TestToSortTracksCmd:
    """Pruebas de `to_sort_tracks_cmd`."""

    def test_disabled_returns_empty(self) -> None:
        """Comprueba que con la ordenación desactivada no se generan argumentos."""
        mixin = _mixin(media=_media(), sort_tracks=False)

        assert mixin.to_sort_tracks_cmd() == []

    def test_empty_media_returns_empty(self) -> None:
        """Comprueba que una media sin streams no genera argumentos."""
        mixin = _mixin(media=_media())

        assert mixin.to_sort_tracks_cmd() == []

    def test_video_only(self) -> None:
        """Comprueba que se mapea la pista de vídeo única."""
        mixin = _mixin(media=_media(video=Video(path=Path("clip.mkv"), track_index=0)))

        assert mixin.to_sort_tracks_cmd() == ["-map", "0:v:0"]

    def test_stream_order_video_audio_subtitles(self) -> None:
        """Comprueba que el orden de salida es vídeo, audio y luego subtítulos."""
        media = _media(
            video=Video(path=Path("clip.mkv"), track_index=0),
            audio=[_audio(language="eng", track_index=0)],
            subtitles=[_subtitle(language="spa", track_index=0)],
        )

        assert _mixin(media=media).to_sort_tracks_cmd() == [
            "-map",
            "0:v:0",
            "-map",
            "0:a:0",
            "-map",
            "0:s:0",
        ]


class TestSortByLanguage:
    """Pruebas del orden de los streams por idioma dentro de cada tipo."""

    def test_audio_sorted_alphabetically(self) -> None:
        """Comprueba que el audio se ordena alfabéticamente por idioma."""
        media = _media(
            audio=[
                _audio(language="spa", track_index=0),
                _audio(language="eng", track_index=1),
                _audio(language="fra", track_index=2),
            ]
        )

        assert _mixin(media=media).to_sort_tracks_cmd() == [
            "-map",
            "0:a:1",
            "-map",
            "0:a:2",
            "-map",
            "0:a:0",
        ]

    def test_language_streams_first(self) -> None:
        """Comprueba que los streams con idioma preceden a los que no lo tienen."""
        media = _media(
            audio=[
                _audio(language=None, track_index=0),
                _audio(language="eng", track_index=1),
            ]
        )

        assert _mixin(media=media).to_sort_tracks_cmd() == [
            "-map",
            "0:a:1",
            "-map",
            "0:a:0",
        ]

    def test_no_language_tracks_keep_order(self) -> None:
        """Comprueba que las pistas sin idioma conservan su orden original."""
        media = _media(
            subtitles=[
                _subtitle(language=None, track_index=0),
                _subtitle(language=None, track_index=1),
                _subtitle(language=None, track_index=2),
            ]
        )

        assert _mixin(media=media).to_sort_tracks_cmd() == [
            "-map",
            "0:s:0",
            "-map",
            "0:s:1",
            "-map",
            "0:s:2",
        ]

    def test_mixed_language_and_no_language(self) -> None:
        """Comprueba que con idioma primero por orden alfabético y luego sin idioma."""
        media = _media(
            audio=[
                _audio(language=None, track_index=0),
                _audio(language="fra", track_index=1),
                _audio(language="deu", track_index=2),
                _audio(language=None, track_index=3),
            ]
        )

        assert _mixin(media=media).to_sort_tracks_cmd() == [
            "-map",
            "0:a:2",
            "-map",
            "0:a:1",
            "-map",
            "0:a:0",
            "-map",
            "0:a:3",
        ]
