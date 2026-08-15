"""Tests para la generación del comando ffmpeg de concat demux
(pymedia.ffmpeg.concat_demux_cmd)."""

from pathlib import Path

from utils.factories import reset_state

from pymedia.cli_params import OutputOnConflictMode
from pymedia.ffmpeg.concat_demux_cmd import concat_demux_cmd


def _setup_state(*, output=None, on_conflict=None):
    state = reset_state()
    state.output = output or Path("out.mp4")
    state.output_on_conflict = on_conflict
    return state


class TestConcatDemuxCmd:
    def test_base_command(self, tmp_path):
        _setup_state()

        cmd = concat_demux_cmd(tmp_path / "list.txt")

        assert cmd == [
            "ffmpeg",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str((tmp_path / "list.txt").absolute()),
            "-c",
            "copy",
            "-progress",
            "pipe:1",
            "-nostats",
            "out.mp4",
        ]

    def test_replace_adds_y(self, tmp_path):
        _setup_state(on_conflict=OutputOnConflictMode.REPLACE)

        cmd = concat_demux_cmd(tmp_path / "list.txt")

        assert cmd[1] == "-y"

    def test_no_y_when_not_replace(self, tmp_path):
        _setup_state(on_conflict=OutputOnConflictMode.FAIL)

        cmd = concat_demux_cmd(tmp_path / "list.txt")

        assert "-y" not in cmd

    def test_output_is_last_argument(self, tmp_path):
        _setup_state()

        cmd = concat_demux_cmd(tmp_path / "list.txt")

        assert cmd[-1] == "out.mp4"
        assert cmd[-2] == "-nostats"
        assert cmd[-3] == "pipe:1"
        assert cmd[-4] == "-progress"

    def test_uses_list_txt(self, tmp_path):
        _setup_state()

        cmd = concat_demux_cmd(tmp_path / "list.txt")

        assert cmd[cmd.index("-i") + 1] == str(
            (tmp_path / "list.txt").absolute()
        )
