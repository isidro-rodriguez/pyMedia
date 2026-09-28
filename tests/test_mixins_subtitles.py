"""Tests para los mixins de subtítulos (pymedia.mixins.subtitles_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import MissingParameterError, UserError
from pymedia.mixins.subtitles_mixin import (
    SubtitlesInputMixin,
    SubtitlesMetadataMixin,
    _find_subtitles_track,
)
from pymedia.models.media import Media
from pymedia.models.subtitles import (
    Subtitles,
    SubtitlesDispositions,
    SubtitlesMetadata,
)


def _subtitles(
    track_index: int | None = 0,
    default: bool | None = None,
    forced: bool | None = None,
    hearing_impaired: bool | None = None,
    visual_impaired: bool | None = None,
    language: str | None = None,
    title: str | None = None,
) -> Subtitles:
    """Pista de subtítulos con los metadatos indicados."""
    return Subtitles(
        path=Path("clip.mkv"),
        track_index=track_index,
        metadata=SubtitlesMetadata(language=language, title=title),
        dispositions=SubtitlesDispositions(
            default=default,
            forced=forced,
            hearing_impaired=hearing_impaired,
            visual_impaired=visual_impaired,
        ),
    )


def _media(subtitles: list[Subtitles] | None = None) -> Media:
    """Media con las pistas de subtítulos indicadas."""
    return Media(path=Path("clip.mkv"), subtitles=subtitles)


def _edit_mixin(*tracks: Subtitles) -> SubtitlesMetadataMixin:
    """SubtitlesMetadataMixin posicionado en la primera pista de `tracks`."""
    return SubtitlesMetadataMixin(media=_media(list(tracks)), stream_tracks=[0])


def _edited(mixin: SubtitlesMetadataMixin) -> Subtitles:
    """Pista editada por el mixin (la primera del medio)."""
    assert mixin.subtitles is not None
    return mixin.subtitles


class TestProcessCodec:
    """Pruebas de `SubtitlesInputMixin._process_codec`."""

    @pytest.mark.parametrize(
        ("suffix", "expected"),
        [
            (".mp4", "mov_text"),
            (".mov", "mov_text"),
            (".m2ts", "mov_text"),
            (".ts", "mov_text"),
            (".mkv", "srt"),
            (".webm", "webvtt"),
        ],
    )
    def test_known_container_maps_to_codec(self, suffix: str, expected: str) -> None:
        """Cada contenedor soportado se traduce a su códec de subtítulos."""
        mixin = SubtitlesInputMixin(media_output=Path(f"salida{suffix}"))

        assert mixin._process_codec() == expected

    def test_unsupported_container_raises_user_error(self) -> None:
        """Un contenedor sin códec de subtítulos lanza un error de usuario."""
        mixin = SubtitlesInputMixin(media_output=Path("salida.avi"))

        with pytest.raises(UserError):
            mixin._process_codec()

    def test_missing_output_raises_missing_parameter(self) -> None:
        """Sin ruta de salida la resolución del códec no puede hacerse."""
        mixin = SubtitlesInputMixin(media_output=None)

        with pytest.raises(MissingParameterError):
            mixin._process_codec()


class TestCreateEditSubtitles:
    """Pruebas de `SubtitlesMetadataMixin.create_edit_subtitles`."""

    def test_forced_sets_flag(self) -> None:
        """`forced` se aplica a la pista y marca la disposición."""
        mixin = _edit_mixin(_subtitles())

        mixin.create_edit_subtitles(forced=True)

        assert _edited(mixin).dispositions.forced is True
        assert mixin.forced is True
        assert mixin.disposition_touched is True

    def test_hearing_impaired_sets_flag(self) -> None:
        """`hearing_impaired` se aplica a la pista y marca la disposición."""
        mixin = _edit_mixin(_subtitles())

        mixin.create_edit_subtitles(hearing_impaired=True)

        assert _edited(mixin).dispositions.hearing_impaired is True
        assert mixin.hearing_impaired is True
        assert mixin.disposition_touched is True

    def test_visual_impaired_sets_flag(self) -> None:
        """`visual_impaired` se aplica a la pista y marca la disposición."""
        mixin = _edit_mixin(_subtitles())

        mixin.create_edit_subtitles(visual_impaired=True)

        assert _edited(mixin).dispositions.visual_impaired is True
        assert mixin.visual_impaired is True
        assert mixin.disposition_touched is True

    def test_language_sets_native_title_when_absent(self) -> None:
        """Indicar el idioma genera el título nativo si no hay ninguno."""
        mixin = _edit_mixin(_subtitles())

        mixin.create_edit_subtitles(language="spa")

        assert _edited(mixin).metadata.language == "spa"
        assert _edited(mixin).metadata.title == "Español"

    def test_language_keeps_existing_title(self) -> None:
        """Un título ya presente no se sobrescribe al cambiar el idioma."""
        mixin = _edit_mixin(_subtitles(title="Audiodescripción"))

        mixin.create_edit_subtitles(language="spa")

        assert _edited(mixin).metadata.language == "spa"
        assert _edited(mixin).metadata.title == "Audiodescripción"


class TestToExclusiveDefaultCmd:
    """Pruebas de `SubtitlesMetadataMixin.to_exclusive_default_cmd`."""

    def test_not_default_returns_empty(self) -> None:
        """Si la pista editada no es `default` no se reescribe ninguna otra."""
        mixin = SubtitlesMetadataMixin(
            media=_media(
                [_subtitles(track_index=0), _subtitles(track_index=1, default=True)]
            ),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == []

    def test_other_default_tracks_are_rewritten(self) -> None:
        """Las demás pistas `default` pierden el flag, conservando el resto."""
        mixin = SubtitlesMetadataMixin(
            media=_media(
                [
                    _subtitles(track_index=0, default=True),
                    _subtitles(track_index=1, default=True, forced=True),
                ]
            ),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == [
            "-disposition:s:1",
            "forced",
        ]

    def test_other_default_track_without_flags_becomes_zero(self) -> None:
        """Una pista `default` sin otros flags se reescribe como `0`."""
        mixin = SubtitlesMetadataMixin(
            media=_media(
                [
                    _subtitles(track_index=0, default=True),
                    _subtitles(track_index=1, default=True),
                ]
            ),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == [
            "-disposition:s:1",
            "0",
        ]

    def test_track_without_index_is_skipped(self) -> None:
        """Las pistas sin `track_index` no se reescriben."""
        mixin = SubtitlesMetadataMixin(
            media=_media(
                [
                    _subtitles(track_index=0, default=True),
                    _subtitles(track_index=None, default=True),
                ]
            ),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == []


class TestFindSubtitlesTrack:
    """Pruebas de `_find_subtitles_track`."""

    def test_existing_index_returns_track(self) -> None:
        """El índice existente devuelve su pista."""
        track = _subtitles(track_index=1)
        media = _media([_subtitles(track_index=0), track])

        assert _find_subtitles_track(media=media, track_index=1) is track

    def test_missing_index_raises_user_error(self) -> None:
        """Un índice inexistente lanza un error de usuario."""
        media = _media([_subtitles(track_index=0)])

        with pytest.raises(UserError):
            _find_subtitles_track(media=media, track_index=9)

    def test_no_subtitles_raises_missing_parameter(self) -> None:
        """Un medio sin pistas de subtítulos no puede resolverse."""
        with pytest.raises(MissingParameterError):
            _find_subtitles_track(media=_media(None), track_index=0)
