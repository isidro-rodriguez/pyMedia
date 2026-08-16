"""Tests para la generación del comando ffmpeg de gif (pymedia.ffmpeg.gif_cmd)."""

from pathlib import Path

from utils.factories import reset_state

from pymedia.cli_params import OutputOnConflictMode
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.models.gif_pipeline import GifPipeline


def _setup_state(*, pipeline=None, inputs=None, on_conflict=None):
    state = reset_state()
    state.gif_pipeline = pipeline or GifPipeline(fps=10)
    state.inputs = inputs or [Path("input.mp4")]
    state.output_on_conflict = on_conflict
    return state


class TestGifCmd:
    def test_base_command(self):
        _setup_state()

        cmd = gif_cmd(Path("out.gif"))

        assert cmd == [
            "ffmpeg",
            "-i",
            "input.mp4",
            "-filter_complex",
            "fps=10,split[a][b];[a]palettegen[p];"
            "[b][p]paletteuse=dither=floyd_steinberg",
            "-progress",
            "pipe:1",
            "-nostats",
            "out.gif",
        ]

    def test_with_crop(self):
        _setup_state(pipeline=GifPipeline(crop=["crop=1520:1080:200:0"], fps=10))

        cmd = gif_cmd(Path("out.gif"))

        filter_complex = cmd[cmd.index("-filter_complex") + 1]
        assert filter_complex.startswith("crop=1520:1080:200:0,")

    def test_with_gyrate(self):
        _setup_state(pipeline=GifPipeline(gyrate="transpose=1", fps=10))

        cmd = gif_cmd(Path("out.gif"))

        filter_complex = cmd[cmd.index("-filter_complex") + 1]
        assert filter_complex.startswith("transpose=1,")

    def test_with_scale(self):
        _setup_state(pipeline=GifPipeline(scale=["scale=-2:720"], fps=10))

        cmd = gif_cmd(Path("out.gif"))

        filter_complex = cmd[cmd.index("-filter_complex") + 1]
        assert filter_complex.startswith("scale=-2:720,")

    def test_with_multiple_filters_joined(self):
        _setup_state(
            pipeline=GifPipeline(
                crop=["crop=1520:1080:200:0"],
                gyrate="transpose=1",
                scale=["scale=-2:720"],
                fps=10,
            )
        )

        cmd = gif_cmd(Path("out.gif"))

        filter_complex = cmd[cmd.index("-filter_complex") + 1]
        assert filter_complex.startswith(
            "crop=1520:1080:200:0,transpose=1,scale=-2:720,"
        )

    def test_replace_adds_y(self):
        _setup_state(on_conflict=OutputOnConflictMode.REPLACE)

        cmd = gif_cmd(Path("out.gif"))

        assert cmd[1] == "-y"

    def test_no_y_when_not_replace(self):
        _setup_state(on_conflict=OutputOnConflictMode.FAIL)

        cmd = gif_cmd(Path("out.gif"))

        assert "-y" not in cmd

    def test_with_start_point(self):
        _setup_state(pipeline=GifPipeline(start_point=10.5, fps=10))

        cmd = gif_cmd(Path("out.gif"))

        assert "-ss" in cmd
        assert cmd[cmd.index("-ss") + 1] == "10.5"

    def test_with_end_point(self):
        _setup_state(pipeline=GifPipeline(end_point=5.0, fps=10))

        cmd = gif_cmd(Path("out.gif"))

        assert "-to" in cmd
        assert cmd[cmd.index("-to") + 1] == "5.0"

    def test_with_start_point_and_end_point(self):
        _setup_state(
            pipeline=GifPipeline(start_point=10.5, end_point=5.0, fps=10)
        )

        cmd = gif_cmd(Path("out.gif"))

        assert "-ss" in cmd
        assert cmd[cmd.index("-ss") + 1] == "10.5"
        assert "-to" in cmd
        assert cmd[cmd.index("-to") + 1] == "5.0"

    def test_output_is_last_argument(self):
        _setup_state()

        cmd = gif_cmd(Path("output/dir/final.gif"))

        assert cmd[-1] == str(Path("output/dir/final.gif"))
        assert cmd[-2] == "-nostats"
        assert cmd[-3] == "pipe:1"
        assert cmd[-4] == "-progress"

    def test_uses_first_input(self):
        _setup_state(inputs=[Path("a.mp4"), Path("b.mp4")])

        cmd = gif_cmd(Path("out.gif"))

        assert cmd[cmd.index("-i") + 1] == "a.mp4"

    def test_scale_with_none_first_element(self):
        _setup_state(
            pipeline=GifPipeline(scale=[None, "scale=-2:720"], fps=10)
        )

        cmd = gif_cmd(Path("out.gif"))

        filter_complex = cmd[cmd.index("-filter_complex") + 1]
        assert "scale=" not in filter_complex

    def test_filter_complex_contains_paletteuse(self):
        _setup_state()

        cmd = gif_cmd(Path("out.gif"))

        filter_complex = cmd[cmd.index("-filter_complex") + 1]
        assert "paletteuse=dither=floyd_steinberg" in filter_complex
