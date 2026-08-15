"""Tests para la generación del comando ffmpeg de concat filter
(pymedia.ffmpeg.concat_filter_cmd)."""

from fractions import Fraction
from pathlib import Path

import pytest

from utils.factories import make_audio, make_config, make_media, make_video, reset_state

from pymedia.cli_params import OutputOnConflictMode, ScaleVideoMode
from pymedia.errors import InvalidConfigError, InvalidSettingError
from pymedia.ffmpeg.concat_filter_cmd import concat_filter_cmd
from pymedia.models.arguments import Arguments, CommandName
from pymedia.models.video_pipeline import VideoPipeline


def _setup_state(
    *,
    media=None,
    inputs=None,
    output=None,
    pipeline=None,
    arguments=None,
    on_conflict=None,
    config=None,
):
    """Configura el state global con valores por defecto razonables."""
    state = reset_state(config=config)
    state.media = media or [
        make_media(video=make_video(), audio=make_audio()),
        make_media(video=make_video(), audio=make_audio()),
    ]
    state.inputs = inputs or [Path("a.mp4"), Path("b.mp4")]
    state.output = output or Path("out.mp4")
    state.video_pipeline = pipeline or VideoPipeline()
    state.arguments = arguments
    state.output_on_conflict = on_conflict
    return state


class TestConcatFilterCmdBase:
    def test_base_command(self):
        _setup_state()

        cmd = concat_filter_cmd()

        assert cmd[0] == "ffmpeg"
        assert "-nostdin" in cmd
        assert "-loglevel" in cmd
        assert cmd[cmd.index("-loglevel") + 1] == "error"
        assert "-filter_complex" in cmd
        assert "-c:v" in cmd
        assert cmd[cmd.index("-c:v") + 1] == "libx264"
        assert "-preset" in cmd
        assert cmd[cmd.index("-preset") + 1] == "medium"
        assert "-crf" in cmd
        assert cmd[cmd.index("-crf") + 1] == "23"
        assert "-threads" in cmd
        assert cmd[cmd.index("-threads") + 1] == "1"
        assert "-progress" in cmd
        assert cmd[cmd.index("-progress") + 1] == "pipe:1"
        assert "-nostats" in cmd
        assert cmd[-1] == Path("out.mp4")

    def test_replace_adds_y(self):
        _setup_state(on_conflict=OutputOnConflictMode.REPLACE)

        cmd = concat_filter_cmd()

        assert cmd[4] == "-y"

    def test_no_y_when_not_replace(self):
        _setup_state(on_conflict=OutputOnConflictMode.FAIL)

        cmd = concat_filter_cmd()

        assert "-y" not in cmd

    def test_output_is_last_argument(self):
        _setup_state(output=Path("output/dir/final.mkv"))

        cmd = concat_filter_cmd()

        assert cmd[-1] == Path("output/dir/final.mkv")
        assert cmd[-2] == "-nostats"
        assert cmd[-3] == "pipe:1"
        assert cmd[-4] == "-progress"


class TestConcatFilterCmdInputs:
    def test_uses_inputs(self):
        _setup_state(inputs=[Path("a.mp4"), Path("b.mp4")])

        cmd = concat_filter_cmd()

        # Two -i flags, one per input
        i_indices = [i for i, v in enumerate(cmd) if v == "-i"]
        assert len(i_indices) == 2
        assert cmd[i_indices[0] + 1] == "a.mp4"
        assert cmd[i_indices[1] + 1] == "b.mp4"

    def test_multiple_inputs(self):
        _setup_state(
            media=[
                make_media(video=make_video(), audio=make_audio()),
                make_media(video=make_video(), audio=make_audio()),
                make_media(video=make_video(), audio=make_audio()),
            ],
            inputs=[Path("a.mp4"), Path("b.mp4"), Path("c.mp4")],
        )

        cmd = concat_filter_cmd()

        i_indices = [i for i, v in enumerate(cmd) if v == "-i"]
        assert len(i_indices) == 3
        assert cmd[i_indices[0] + 1] == "a.mp4"
        assert cmd[i_indices[1] + 1] == "b.mp4"
        assert cmd[i_indices[2] + 1] == "c.mp4"


class TestConcatFilterCmdVideoChain:
    def test_no_scale_when_same_height(self):
        """Videos with same height and no explicit scale → no scale filter."""
        _setup_state(
            media=[
                make_media(video=make_video(width=1920, height=1080), audio=make_audio()),
                make_media(video=make_video(width=1920, height=1080), audio=make_audio()),
            ],
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        # No scale= in the filter graph
        assert "scale=" not in filters
        # But normalization is present
        assert "setsar=1" in filters
        assert "setpts=PTS-STARTPTS" in filters

    def test_scale_when_different_heights(self):
        """Videos with different heights → scale to min height."""
        _setup_state(
            media=[
                make_media(
                    video=make_video(width=1920, height=1080), audio=make_audio()
                ),
                make_media(
                    video=make_video(width=1280, height=720), audio=make_audio()
                ),
            ],
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        # Both inputs should have scale filter
        assert "scale=1280:720" in filters  # 1920*720/1080 = 1280
        assert "scale=1280:720" in filters

    def test_gyrate_filter(self):
        _setup_state(
            pipeline=VideoPipeline(gyrate="transpose=1"),
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        assert "transpose=1" in filters

    def test_crop_filter(self):
        _setup_state(
            pipeline=VideoPipeline(crop=["crop=1520:1080:200:0", "crop=1520:1080:200:0"]),
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        assert "crop=1520:1080:200:0" in filters


class TestConcatFilterCmdAudioChain:
    def test_audio_compatible(self):
        """Identical audio → only asetpts reset."""
        _setup_state(
            media=[
                make_media(
                    video=make_video(),
                    audio=make_audio(
                        codec="aac", sample_rate=48000, channels=2, channel_layout="stereo"
                    ),
                ),
                make_media(
                    video=make_video(),
                    audio=make_audio(
                        codec="aac", sample_rate=48000, channels=2, channel_layout="stereo"
                    ),
                ),
            ],
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        assert "aresample=48000" not in filters
        assert "aformat=" not in filters
        assert "asetpts=PTS-STARTPTS" in filters
        # Audio is mapped
        assert "-map" in cmd
        assert "[a]" in cmd

    def test_audio_incompatible(self):
        """Different audio → aresample + aformat normalization."""
        _setup_state(
            media=[
                make_media(
                    video=make_video(),
                    audio=make_audio(
                        codec="aac", sample_rate=48000, channels=2, channel_layout="stereo"
                    ),
                ),
                make_media(
                    video=make_video(),
                    audio=make_audio(
                        codec="aac", sample_rate=44100, channels=1, channel_layout="mono"
                    ),
                ),
            ],
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        assert "aresample=48000" in filters
        assert "aformat=sample_fmts=fltp:channel_layouts=stereo" in filters
        assert "asetpts=PTS-STARTPTS" in filters

    def test_no_audio(self):
        """No audio in any input → concat with a=0."""
        _setup_state(
            media=[
                make_media(video=make_video()),
                make_media(video=make_video()),
            ],
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        assert "concat=n=2:v=1:a=0" in filters
        assert "-c:a" not in cmd
        assert "[a]" not in cmd


class TestConcatFilterCmdConfig:
    def test_uses_config_codec_values(self):
        _setup_state(
            config=make_config(
                video_codec="h265",
                video_preset="slow",
                video_crf=28,
                audio_codec="aac",
            ),
        )

        cmd = concat_filter_cmd()

        assert cmd[cmd.index("-c:v") + 1] == "libx265"
        assert cmd[cmd.index("-preset") + 1] == "slow"
        assert cmd[cmd.index("-crf") + 1] == "28"
        assert cmd[cmd.index("-c:a") + 1] == "aac"

    def test_uses_av1_codec_values(self):
        _setup_state(
            config=make_config(
                video_codec="av1",
                video_preset="5",
                video_crf=32,
            ),
        )

        cmd = concat_filter_cmd()

        assert cmd[cmd.index("-c:v") + 1] == "libsvtav1"
        assert cmd[cmd.index("-preset") + 1] == "5"
        assert cmd[cmd.index("-crf") + 1] == "32"

    def test_min_fps(self):
        _setup_state(
            media=[
                make_media(video=make_video(fps=Fraction(25, 1)), audio=make_audio()),
                make_media(video=make_video(fps=Fraction(30, 1)), audio=make_audio()),
            ],
            config=make_config(fps="min_fps"),
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        assert "fps=25" in filters

    def test_max_fps(self):
        _setup_state(
            media=[
                make_media(video=make_video(fps=Fraction(25, 1)), audio=make_audio()),
                make_media(video=make_video(fps=Fraction(30, 1)), audio=make_audio()),
            ],
            config=make_config(fps="max_fps"),
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        assert "fps=30" in filters

    def test_min_height(self):
        _setup_state(
            media=[
                make_media(
                    video=make_video(width=1920, height=1080), audio=make_audio()
                ),
                make_media(
                    video=make_video(width=1280, height=720), audio=make_audio()
                ),
            ],
            config=make_config(resize_to="min_height"),
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        # min height is 720, width proportional: 1920*720/1080 = 1280
        assert "scale=1280:720" in filters

    def test_max_height(self):
        _setup_state(
            media=[
                make_media(
                    video=make_video(width=1920, height=1080), audio=make_audio()
                ),
                make_media(
                    video=make_video(width=1280, height=720), audio=make_audio()
                ),
            ],
            config=make_config(resize_to="max_height"),
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        # max height is 1080, width proportional: 1280*1080/720 = 1920
        assert "scale=1920:1080" in filters


class TestConcatFilterCmdScaleArgument:
    def test_explicit_scale_downscales(self):
        """When arguments.scale is smaller than min height, use that value."""
        _setup_state(
            media=[
                make_media(
                    video=make_video(width=1920, height=1080), audio=make_audio()
                ),
                make_media(
                    video=make_video(width=1280, height=720), audio=make_audio()
                ),
            ],
            arguments=Arguments(
                command=CommandName.CONCAT,
                scale=ScaleVideoMode.P480,
            ),
        )

        cmd = concat_filter_cmd()

        filters = cmd[cmd.index("-filter_complex") + 1]
        # scale=480 is smaller than min height (720) → target height = 480
        # width proportional: 1920*480/1080 = 853.33 → round to 854
        assert "scale=854:480" in filters


class TestConcatFilterCmdErrors:
    def test_invalid_fps_raises(self):
        _setup_state(
            config=make_config(fps="invalid_fps"),
        )

        with pytest.raises(InvalidSettingError):
            concat_filter_cmd()

    def test_invalid_resize_to_raises(self):
        _setup_state(
            config=make_config(resize_to="invalid_value"),
        )

        with pytest.raises(InvalidConfigError):
            concat_filter_cmd()
