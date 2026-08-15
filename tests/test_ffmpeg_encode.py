"""Tests para la generación del comando ffmpeg de encode (pymedia.ffmpeg.encode_cmd)."""

from pathlib import Path

from pymedia.cli_params import OutputOnConflictMode
from pymedia.ffmpeg.encode_cmd import encode_cmd
from pymedia.models.video_pipeline import VideoPipeline
from utils.factories import make_config, reset_state


def _setup_state(*, pipeline=None, inputs=None, on_conflict=None):
    state = reset_state()
    state.video_pipeline = pipeline or VideoPipeline()
    state.inputs = inputs or [Path("input.mp4")]
    state.output_on_conflict = on_conflict
    return state


class TestEncodeCmd:
    def test_base_command(self):
        _setup_state()

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert cmd == [
            "ffmpeg",
            "-i",
            "input.mp4",
            "-c:v",
            "libx264",
            "-crf",
            "23",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            "-progress",
            "pipe:1",
            "-nostats",
            "out.mp4",
        ]

    def test_no_filter_when_pipeline_empty(self):
        _setup_state()

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert "-filter:v" not in cmd

    def test_with_crop(self):
        _setup_state(pipeline=VideoPipeline(crop=["crop=1520:1080:200:0"]))

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert "-filter:v" in cmd
        assert cmd[cmd.index("-filter:v") + 1] == "crop=1520:1080:200:0"

    def test_with_gyrate(self):
        _setup_state(pipeline=VideoPipeline(gyrate="transpose=1"))

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert cmd[cmd.index("-filter:v") + 1] == "transpose=1"

    def test_with_scale(self):
        _setup_state(pipeline=VideoPipeline(scale=["scale=-2:720"]))

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert cmd[cmd.index("-filter:v") + 1] == "scale=-2:720"

    def test_with_multiple_filters_joined(self):
        _setup_state(
            pipeline=VideoPipeline(
                crop=["crop=1520:1080:200:0"],
                gyrate="transpose=1",
                scale=["scale=-2:720"],
            ),
        )

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert cmd[cmd.index("-filter:v") + 1] == (
            "crop=1520:1080:200:0,transpose=1,scale=-2:720"
        )

    def test_replace_adds_y(self):
        _setup_state(on_conflict=OutputOnConflictMode.REPLACE)

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert cmd[1] == "-y"

    def test_no_y_when_not_replace(self):
        _setup_state(on_conflict=OutputOnConflictMode.FAIL)

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert "-y" not in cmd

    def test_uses_config_codec_values(self):
        state = _setup_state()
        state.config = make_config(
            video_codec="av1",
            video_preset="5",
            video_crf=32,
        )

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert cmd[cmd.index("-c:v") + 1] == "libsvtav1"
        assert cmd[cmd.index("-crf") + 1] == "32"
        assert cmd[cmd.index("-preset") + 1] == "5"
        assert cmd[cmd.index("-pix_fmt") + 1] == "yuv420p10le"

    def test_uses_h265_codec_values(self):
        state = _setup_state()
        state.config = make_config(
            video_codec="h265",
            video_preset="slow",
            video_crf=28,
        )

        cmd = encode_cmd(Path("input.mp4"), Path("out.mp4"))

        assert cmd[cmd.index("-c:v") + 1] == "libx265"
        assert cmd[cmd.index("-crf") + 1] == "28"
        assert cmd[cmd.index("-preset") + 1] == "slow"
        assert cmd[cmd.index("-pix_fmt") + 1] == "yuv420p10le"

    def test_index_uses_inputs_position(self):
        _setup_state(
            pipeline=VideoPipeline(crop=["crop=1:1:0:0", "crop=2:2:0:0"]),
            inputs=[Path("a.mp4"), Path("b.mp4")],
        )

        cmd = encode_cmd(Path("b.mp4"), Path("out.mp4"))

        assert cmd[cmd.index("-filter:v") + 1] == "crop=2:2:0:0"

    def test_scale_uses_inputs_position(self):
        _setup_state(
            pipeline=VideoPipeline(scale=["scale=-2:480", "scale=-2:720"]),
            inputs=[Path("a.mp4"), Path("b.mp4")],
        )

        cmd = encode_cmd(Path("b.mp4"), Path("out.mp4"))

        assert cmd[cmd.index("-filter:v") + 1] == "scale=-2:720"

    def test_output_is_last_argument(self):
        _setup_state()

        cmd = encode_cmd(Path("input.mp4"), Path("output/dir/final.mkv"))

        assert cmd[-1] == str(Path("output/dir/final.mkv"))
        assert cmd[-2] == "-nostats"
        assert cmd[-3] == "pipe:1"
        assert cmd[-4] == "-progress"
