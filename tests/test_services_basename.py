"""Tests para el servicio de nombres de fichero (pymedia.services.basename_service)."""

from pathlib import Path

import pytest

from pymedia.errors import (
    InvalidDirectoryError,
    InvalidFileExtensionError,
    InvalidFileNameError,
    InvalidGifExtensionError,
    InvalidVideoExtensionError,
    MissingMediaPropertyError,
)
from pymedia.models.arguments import CommandName
from pymedia.services.basename_service import process_inputs, process_output

# -----------------------------------------------------------------------------
#  process_inputs()
# -----------------------------------------------------------------------------


class TestProcessInputs:
    def test_valid_single_input(self):
        result = process_inputs([Path("video.mp4")])

        assert result == [Path("video.mp4")]

    def test_valid_multiple_inputs(self):
        inputs = [Path("a.mkv"), Path("b.mov"), Path("c.webm")]

        result = process_inputs(inputs)

        assert result == inputs

    def test_invalid_extension_raises(self):
        with pytest.raises(InvalidVideoExtensionError):
            process_inputs([Path("video.txt")])

    def test_no_extension_raises(self):
        with pytest.raises(InvalidVideoExtensionError):
            process_inputs([Path("video")])

    def test_one_invalid_among_valid_raises(self):
        with pytest.raises(InvalidVideoExtensionError):
            process_inputs([Path("a.mp4"), Path("b.xyz")])


# -----------------------------------------------------------------------------
#  process_output()
# -----------------------------------------------------------------------------


class TestProcessOutput:
    def test_valid_video_output(self, tmp_path):
        out = tmp_path / "sub" / "out.mp4"

        result = process_output(
            out,
            CommandName.ENCODE,
            target_video_codec="h264",
            target_audio_codec="aac",
        )

        assert result == out
        assert out.parent.exists()

    def test_valid_gif_output(self, tmp_path):
        out = tmp_path / "out.gif"

        result = process_output(out, CommandName.GIF)

        assert result == out

    def test_gif_with_non_gif_extension_raises(self, tmp_path):
        with pytest.raises(InvalidGifExtensionError):
            process_output(tmp_path / "out.mp4", CommandName.GIF)

    def test_video_extension_not_in_containers_raises(self, tmp_path):
        with pytest.raises(InvalidVideoExtensionError):
            process_output(
                tmp_path / "out.txt",
                CommandName.ENCODE,
                target_video_codec="h264",
                target_audio_codec="aac",
            )

    def test_missing_video_codec_raises(self, tmp_path):
        with pytest.raises(MissingMediaPropertyError):
            process_output(
                tmp_path / "out.mp4",
                CommandName.ENCODE,
                target_video_codec=None,
                target_audio_codec="aac",
            )

    def test_video_codec_unsupported_container_raises(self, tmp_path):
        with pytest.raises(InvalidFileExtensionError):
            process_output(
                tmp_path / "out.webm",
                CommandName.ENCODE,
                target_video_codec="h264",
                target_audio_codec="aac",
            )

    def test_audio_codec_unsupported_container_raises(self, tmp_path):
        with pytest.raises(InvalidFileExtensionError):
            process_output(
                tmp_path / "out.mp4",
                CommandName.ENCODE,
                target_video_codec="h264",
                target_audio_codec="ac3",
            )

    def test_audio_codec_none_ok(self, tmp_path):
        out = tmp_path / "out.mp4"

        result = process_output(
            out,
            CommandName.ENCODE,
            target_video_codec="h264",
            target_audio_codec=None,
        )

        assert result == out

    def test_invalid_filename_raises(self, tmp_path):
        with pytest.raises(InvalidFileNameError):
            process_output(tmp_path / "bad<name.mp4", CommandName.ENCODE)

    def test_reserved_windows_name_raises(self, tmp_path):
        with pytest.raises(InvalidFileNameError):
            process_output(tmp_path / "con.mp4", CommandName.ENCODE)

    def test_invalid_directory_raises(self, tmp_path):
        with pytest.raises(InvalidDirectoryError):
            process_output(Path("bad|dir/out.mp4"), CommandName.ENCODE)