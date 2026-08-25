"""Tests para los mixins de salida (pymedia.models.mixins.outputs_mixin)."""

from pathlib import Path

import pytest

from pymedia.errors import (
    ConflictiveOutputParametersError,
    InvalidContainerTypeError,
    InvalidFileExtensionError,
    InvalidNameError,
    MissingMediaError,
    MissingMediaPropertyError,
    OutputParameterError,
)
from pymedia.models.enums import OutputMediaType
from pymedia.models.media import Audio, Media, Video
from pymedia.models.mixins.outputs_mixin import (
    OutputBatchMixin,
    OutputSingleMixin,
    _process_output,
    _validate_name,
)


def _video(codec: str | None = "h264") -> Video:
    """Vídeo de ayuda con códec h264 por defecto."""
    return Video(codec=codec, width=1920, height=1080)


def _audio(codec: str | None = "aac") -> Audio:
    """Pista de audio de ayuda con códec aac por defecto."""
    return Audio(codec=codec, sample_rate=48000, channels=2)


def _media(video: Video | None = None, audio: Audio | None = None) -> Media:
    """Media de ayuda con vídeo h264 y audio opcional."""
    return Media(video=video, audio=audio)


def _single_mixin(
    input_single: Path = Path("clip.mp4"), media: Media | None = None
) -> OutputSingleMixin:
    """OutputSingleMixin con entrada y media de ayuda."""
    mixin = OutputSingleMixin()
    mixin.input_single = input_single
    mixin.media = media
    return mixin


def _batch_mixin(
    inputs: list[Path], media_list: list[Media | None] | None = None
) -> OutputBatchMixin:
    """OutputBatchMixin con las entradas y metadatos indicados."""
    mixin = OutputBatchMixin()
    mixin.input_list = list(inputs)
    mixin.media_list = (
        media_list if media_list is not None else [_media() for _ in inputs]
    )
    mixin.media = mixin.media_list[0] if mixin.media_list else None
    return mixin


class TestValidateName:
    @pytest.mark.parametrize("name", ["clip", "clip final", "Clip-01_v2", "vídeo ñ"])
    def test_valid_names_do_not_raise(self, name):
        _validate_name(name)

    @pytest.mark.parametrize(
        "name",
        ["a<b", "a>b", "a:b", 'a"b', "a/b", "a\\b", "a|b", "a?b", "a*b", "a\x00b"],
    )
    def test_invalid_characters(self, name):
        with pytest.raises(InvalidNameError):
            _validate_name(name)

    @pytest.mark.parametrize(
        "name", ["CON", "con", "PRN", "AUX", "NUL", "LPT1", "COM9"]
    )
    def test_reserved_names(self, name):
        with pytest.raises(InvalidNameError):
            _validate_name(name)

    @pytest.mark.parametrize("name", ["clip ", "clip."])
    def test_trailing_space_or_dot(self, name):
        with pytest.raises(InvalidNameError):
            _validate_name(name)

    def test_empty_name(self):
        with pytest.raises(InvalidNameError):
            _validate_name("")


class TestProcessOutput:
    def test_default_path_uses_input_name(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        output = _process_output(
            Path("clip.mp4"),
            _media(),
            OutputMediaType.GIF,
            extension=".gif",
        )

        assert output == (tmp_path / "clip.gif").absolute()

    def test_affix_and_extension_applied(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        output = _process_output(
            Path("clip.mp4"),
            _media(),
            OutputMediaType.GIF,
            affix="_edit",
            extension=".gif",
        )

        assert output == (tmp_path / "clip_edit.gif").absolute()

    def test_explicit_output_ignores_affix(self, tmp_path):
        explicit = tmp_path / "done.gif"

        output = _process_output(
            Path("clip.mp4"),
            _media(),
            OutputMediaType.GIF,
            affix="_x",
            extension=".gif",
            output=explicit,
        )

        assert output == explicit.absolute()


class TestValidateOutput:
    def test_gif_valid_extension(self, tmp_path):
        mixin = _single_mixin(media=_media())

        mixin.create_output_single(OutputMediaType.GIF, output=tmp_path / "out.gif")

        assert mixin.output == (tmp_path / "out.gif").absolute()

    def test_gif_invalid_extension(self, tmp_path):
        mixin = _single_mixin(media=_media())

        with pytest.raises(InvalidContainerTypeError) as exc_info:
            mixin.create_output_single(OutputMediaType.GIF, output=tmp_path / "out.png")

        assert "gif" in exc_info.value.message

    def test_image_valid_extension(self, tmp_path):
        mixin = _single_mixin()

        mixin.create_output_single(OutputMediaType.IMAGE, output=tmp_path / "out.png")

        assert mixin.output == (tmp_path / "out.png").absolute()

    def test_image_invalid_extension(self, tmp_path):
        mixin = _single_mixin()

        with pytest.raises(InvalidContainerTypeError) as exc_info:
            mixin.create_output_single(
                OutputMediaType.IMAGE, output=tmp_path / "out.xyz"
            )

        assert "Image" in exc_info.value.message

    def test_audio_requires_track(self, tmp_path):
        mixin = _single_mixin(media=_media(audio=None))

        with pytest.raises(MissingMediaPropertyError, match="audio track"):
            mixin.create_output_single(
                OutputMediaType.AUDIO, output=tmp_path / "out.m4a"
            )

    def test_audio_valid_extension(self, tmp_path):
        mixin = _single_mixin(media=_media(audio=_audio("aac")))

        mixin.create_output_single(OutputMediaType.AUDIO, output=tmp_path / "out.m4a")

        assert mixin.output == (tmp_path / "out.m4a").absolute()

    def test_audio_extension_not_supported_by_codec(self, tmp_path):
        mixin = _single_mixin(media=_media(audio=_audio("aac")))

        with pytest.raises(InvalidFileExtensionError):
            mixin.create_output_single(
                OutputMediaType.AUDIO, output=tmp_path / "out.flac"
            )

    def test_audio_not_container_extension(self, tmp_path):
        mixin = _single_mixin(media=_media(audio=_audio("aac")))

        with pytest.raises(InvalidContainerTypeError):
            mixin.create_output_single(
                OutputMediaType.AUDIO, output=tmp_path / "out.txt"
            )

    def test_subtitle_valid_extension(self, tmp_path):
        mixin = _single_mixin()

        mixin.create_output_single(
            OutputMediaType.SUBTITLE, output=tmp_path / "out.srt"
        )

        assert mixin.output == (tmp_path / "out.srt").absolute()

    def test_subtitle_invalid_extension(self, tmp_path):
        mixin = _single_mixin()

        with pytest.raises(InvalidContainerTypeError) as exc_info:
            mixin.create_output_single(
                OutputMediaType.SUBTITLE, output=tmp_path / "out.xyz"
            )

        assert "Subtitle" in exc_info.value.message

    def test_video_requires_track(self, tmp_path):
        mixin = _single_mixin(media=_media(video=None))

        with pytest.raises(MissingMediaPropertyError, match="video"):
            mixin.create_output_single(
                OutputMediaType.VIDEO, output=tmp_path / "out.mp4"
            )

    def test_video_requires_codec(self, tmp_path):
        mixin = _single_mixin(media=_media(video=_video(None)))

        with pytest.raises(MissingMediaPropertyError, match="video codec"):
            mixin.create_output_single(
                OutputMediaType.VIDEO, output=tmp_path / "out.mp4"
            )

    def test_video_valid_extension(self, tmp_path):
        mixin = _single_mixin(media=_media(video=_video("h264")))

        mixin.create_output_single(OutputMediaType.VIDEO, output=tmp_path / "out.mp4")

        assert mixin.output == (tmp_path / "out.mp4").absolute()

    def test_video_extension_not_supported_by_codec(self, tmp_path):
        mixin = _single_mixin(media=_media(video=_video("h264")))

        with pytest.raises(InvalidFileExtensionError) as exc_info:
            mixin.create_output_single(
                OutputMediaType.VIDEO, output=tmp_path / "out.avi"
            )

        assert "h264" in exc_info.value.message

    def test_video_not_container_extension(self, tmp_path):
        mixin = _single_mixin(media=_media(video=_video("h264")))

        with pytest.raises(InvalidContainerTypeError):
            mixin.create_output_single(
                OutputMediaType.VIDEO, output=tmp_path / "out.txt"
            )

    def test_video_audio_codec_checked(self, tmp_path):
        mixin = _single_mixin(media=_media(video=_video("h264"), audio=_audio("aac")))

        # .m2ts es válido para h264 pero no para aac
        with pytest.raises(InvalidFileExtensionError):
            mixin.create_output_single(
                OutputMediaType.VIDEO, output=tmp_path / "out.m2ts"
            )


class TestOutputSingleDefault:
    def test_default_output_named_from_input(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        mixin = _single_mixin(input_single=Path("clip.mp4"))
        mixin.create_output_single(OutputMediaType.GIF, extension=".gif")

        assert mixin.output == (tmp_path / "clip.gif").absolute()

    def test_default_with_affix(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        mixin = _single_mixin(input_single=Path("clip.mp4"))
        mixin.create_output_single(OutputMediaType.GIF, affix="_edit", extension=".gif")

        assert mixin.output == (tmp_path / "clip_edit.gif").absolute()


class TestOutputBatch:
    def test_conflictive_output_and_directory(self, tmp_path):
        mixin = _batch_mixin([Path("a.mp4")])

        with pytest.raises(ConflictiveOutputParametersError):
            mixin.create_output_batch(
                OutputMediaType.GIF,
                output=tmp_path / "o.gif",
                output_directory=tmp_path / "dir",
            )

    def test_output_rejected_with_multiple_inputs(self, tmp_path):
        mixin = _batch_mixin([Path("a.mp4"), Path("b.mp4")])

        with pytest.raises(OutputParameterError):
            mixin.create_output_batch(OutputMediaType.GIF, output=tmp_path / "o.gif")

    def test_output_requires_media(self, tmp_path):
        mixin = _batch_mixin([Path("a.mp4")], media_list=[None])

        with pytest.raises(MissingMediaError):
            mixin.create_output_batch(OutputMediaType.GIF, output=tmp_path / "o.gif")

    def test_output_with_single_input(self, tmp_path):
        mixin = _batch_mixin([Path("a.mp4")])

        mixin.create_output_batch(OutputMediaType.GIF, output=tmp_path / "o.gif")

        assert mixin.output == (tmp_path / "o.gif").absolute()
        assert mixin.output_directory is None

    def test_output_directory_created(self, tmp_path):
        mixin = _batch_mixin([Path("a.mp4"), Path("b.mp4")])
        target = tmp_path / "out"

        mixin.create_output_batch(OutputMediaType.GIF, output_directory=target)

        assert mixin.output_directory == target
        assert target.is_dir()

    def test_output_directory_invalid_name(self, tmp_path):
        mixin = _batch_mixin([Path("a.mp4"), Path("b.mp4")])

        with pytest.raises(InvalidNameError):
            mixin.create_output_batch(
                OutputMediaType.GIF, output_directory=tmp_path / "out<bad>"
            )
