"""Tests para los mixins de audio (pymedia.mixins.audio_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import InvalidCodecContainerError, UserError
from pymedia.mixins.audio_mixin import (
    AudioInputMixin,
    AudioMetadataMixin,
)
from pymedia.models.audio import (
    Audio,
    AudioDispositions,
    AudioFormat,
    AudioMetadata,
)
from pymedia.models.media import Media
from pymedia.models.video import Video


def _audio(
    track_index: int | None = 0,
    codec: str | None = "aac",
    default: bool | None = None,
    forced: bool | None = None,
    hearing_impaired: bool | None = None,
    commentary: bool | None = None,
    language: str | None = None,
    title: str | None = None,
) -> Audio:
    """Pista de audio con los metadatos indicados."""
    return Audio(
        path=Path("clip.mkv"),
        track_index=track_index,
        format=AudioFormat(codec=codec),
        metadata=AudioMetadata(language=language, title=title),
        dispositions=AudioDispositions(
            default=default,
            forced=forced,
            hearing_impaired=hearing_impaired,
            commentary=commentary,
        ),
    )


def _media(audio: list[Audio] | None = None, video: Video | None = None) -> Media:
    """Media con las pistas de audio indicadas."""
    return Media(path=Path("clip.mkv"), video=video, audio=audio)


def _edit_mixin(*tracks: Audio) -> AudioMetadataMixin:
    """AudioMetadataMixin posicionado en la primera pista de `tracks`."""
    return AudioMetadataMixin(media=_media(list(tracks)), stream_tracks=[0])


def _edited(mixin: AudioMetadataMixin) -> Audio:
    """Pista editada por el mixin (la primera del medio)."""
    media = mixin.media
    assert media is not None
    audio = media.audio
    assert audio is not None
    return audio[0]


class TestValidateAudioContainers:
    """Pruebas de `AudioInputMixin.validate_audio_containers`."""

    def test_no_audio_returns_without_error(self) -> None:
        """Sin pistas importadas la validación no hace nada."""
        mixin = AudioInputMixin()
        mixin.audio = None

        mixin.validate_audio_containers(".mp4")

    def test_track_without_codec_is_skipped(self) -> None:
        """Una pista sin códec conocido se omite sin error."""
        mixin = AudioInputMixin(audio=[_audio(codec=None)])

        mixin.validate_audio_containers(".mp4")

    def test_unknown_codec_is_skipped(self) -> None:
        """Un códec fuera del catálogo se omite sin error."""
        mixin = AudioInputMixin(audio=[_audio(codec="desconocido")])

        mixin.validate_audio_containers(".mp4")

    def test_compatible_codec_passes(self) -> None:
        """Un códec compatible con el contenedor no dispara error."""
        mixin = AudioInputMixin(audio=[_audio(codec="aac")])

        mixin.validate_audio_containers(".mp4")

    def test_incompatible_codec_raises(self) -> None:
        """Un códec no admitido por el contenedor lanza el error."""
        # `flac` no está entre los contenedores de `aac`.
        mixin = AudioInputMixin(audio=[_audio(codec="flac")])

        with pytest.raises(InvalidCodecContainerError):
            mixin.validate_audio_containers(".mp4")


class TestCreateEditAudio:
    """Pruebas de `AudioMetadataMixin.create_edit_audio`."""

    def test_hearing_impaired_sets_flag(self) -> None:
        """`hearing_impaired` se aplica a la pista y marca la disposición."""
        mixin = _edit_mixin(_audio())

        mixin.create_edit_audio(hearing_impaired=True)

        assert _edited(mixin).dispositions.hearing_impaired is True
        assert mixin.hearing_impaired is True
        assert mixin.disposition_touched is True

    def test_commentary_sets_flag(self) -> None:
        """`commentary` se aplica a la pista y marca la disposición."""
        mixin = _edit_mixin(_audio())

        mixin.create_edit_audio(commentary=True)

        assert _edited(mixin).dispositions.commentary is True
        assert mixin.commentary is True
        assert mixin.disposition_touched is True

    def test_hearing_impaired_clears_flag(self) -> None:
        """`hearing_impaired=False` limpia la disposición de la pista."""
        mixin = _edit_mixin(_audio(hearing_impaired=True))

        mixin.create_edit_audio(hearing_impaired=False)

        assert _edited(mixin).dispositions.hearing_impaired is False
        assert mixin.disposition_touched is True


class TestToExclusiveDefaultCmd:
    """Pruebas de `AudioMetadataMixin.to_exclusive_default_cmd`."""

    def test_not_default_returns_empty(self) -> None:
        """Si la pista editada no es `default` no se reescribe ninguna otra."""
        mixin = AudioMetadataMixin(
            media=_media([_audio(track_index=0), _audio(track_index=1, default=True)]),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == []

    def test_other_default_tracks_are_rewritten(self) -> None:
        """Las demás pistas `default` pierden el flag, conservando el resto."""
        mixin = AudioMetadataMixin(
            media=_media(
                [
                    _audio(track_index=0, default=True),
                    _audio(track_index=1, default=True, forced=True),
                ]
            ),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == [
            "-disposition:a:1",
            "forced",
        ]

    def test_other_default_track_without_flags_becomes_zero(self) -> None:
        """Una pista `default` sin otros flags se reescribe como `0`."""
        mixin = AudioMetadataMixin(
            media=_media(
                [
                    _audio(track_index=0, default=True),
                    _audio(track_index=1, default=True),
                ]
            ),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == [
            "-disposition:a:1",
            "0",
        ]

    def test_track_without_index_is_skipped(self) -> None:
        """Las pistas sin `track_index` no se reescriben."""
        mixin = AudioMetadataMixin(
            media=_media(
                [
                    _audio(track_index=0, default=True),
                    _audio(track_index=None, default=True),
                ]
            ),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == []

    def test_non_default_tracks_are_untouched(self) -> None:
        """Las pistas sin `default` se conservan intactas."""
        mixin = AudioMetadataMixin(
            media=_media(
                [
                    _audio(track_index=0, default=True),
                    _audio(track_index=1, default=False, forced=True),
                ]
            ),
            stream_tracks=[0],
        )

        assert mixin.to_exclusive_default_cmd() == []


class TestFindAudioTrack:
    """Pruebas de `AudioMetadataMixin.find_audio_track`."""

    def test_existing_index_returns_track(self) -> None:
        """El índice existente devuelve su pista."""
        track = _audio(track_index=1)
        mixin = AudioMetadataMixin(media=_media([_audio(track_index=0), track]))

        assert mixin.find_audio_track(1) is track

    def test_missing_index_raises_user_error(self) -> None:
        """Un índice inexistente lanza un error de usuario."""
        mixin = AudioMetadataMixin(media=_media([_audio(track_index=0)]))

        with pytest.raises(UserError):
            mixin.find_audio_track(9)
