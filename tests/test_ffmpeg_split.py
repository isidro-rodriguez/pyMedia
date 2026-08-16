"""Tests para la generación del comando ffmpeg de split (pymedia.ffmpeg.split_cmd)."""

from utils.factories import reset_state

from pymedia.cli_params import OutputOnConflictMode
from pymedia.ffmpeg.split_cmd import split_cmd
from pymedia.models.video_pipeline import VideoPipeline


def _setup_state(*, pipeline=None, on_conflict=None):
    state = reset_state()
    state.video_pipeline = pipeline or VideoPipeline(trim_points="10,20,30")
    state.output_on_conflict = on_conflict
    return state


class TestSplitCmd:
    def test_base_command(self, tmp_path):
        _setup_state()

        cmd = split_cmd(tmp_path / "input.mp4", tmp_path / "out.mp4")

        assert cmd == [
            "ffmpeg",
            "-i",
            str((tmp_path / "input.mp4").absolute()),
            "-map",
            "0",
            "-c",
            "copy",
            "-f",
            "segment",
            "-reset_timestamps",
            "1",
            "-segment_times",
            "10,20,30",
            "-progress",
            "pipe:1",
            "-nostats",
            str((tmp_path / "out.mp4").absolute()),
        ]

    def test_replace_adds_y(self, tmp_path):
        _setup_state(on_conflict=OutputOnConflictMode.REPLACE)

        cmd = split_cmd(tmp_path / "input.mp4", tmp_path / "out.mp4")

        assert cmd[1] == "-y"

    def test_no_y_when_not_replace(self, tmp_path):
        _setup_state(on_conflict=OutputOnConflictMode.FAIL)

        cmd = split_cmd(tmp_path / "input.mp4", tmp_path / "out.mp4")

        assert "-y" not in cmd

    def test_output_is_last_argument(self, tmp_path):
        _setup_state()

        cmd = split_cmd(tmp_path / "input.mp4", tmp_path / "out.mp4")

        assert cmd[-1] == str((tmp_path / "out.mp4").absolute())
        assert cmd[-2] == "-nostats"
        assert cmd[-3] == "pipe:1"
        assert cmd[-4] == "-progress"

    def test_uses_input(self, tmp_path):
        _setup_state()

        cmd = split_cmd(tmp_path / "input.mp4", tmp_path / "out.mp4")

        assert cmd[cmd.index("-i") + 1] == str((tmp_path / "input.mp4").absolute())

    def test_segment_times_from_pipeline(self, tmp_path):
        _setup_state(pipeline=VideoPipeline(trim_points="00:10,00:20,00:30"))

        cmd = split_cmd(tmp_path / "input.mp4", tmp_path / "out.mp4")

        assert cmd[cmd.index("-segment_times") + 1] == "00:10,00:20,00:30"

    def test_video_outputs_naming(self, tmp_path):
        _setup_state()

        cmd = split_cmd(tmp_path / "input.mp4", tmp_path / "out.mp4")

        # split_cmd uses the output path as-is (no _%02d suffix)
        assert cmd[-1] == str((tmp_path / "out.mp4").absolute())
