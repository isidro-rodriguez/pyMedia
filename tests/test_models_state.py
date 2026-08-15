"""Tests para el modelo de estado global (pymedia.models.state)."""

from pathlib import Path

import pytest

from pymedia.cli_params import OutputOnConflictMode
from pymedia.errors import InvalidVideoExtensionError, MissingArgumentsError, MissingMediaError
from pymedia.models.arguments import Arguments, CommandName
from pymedia.models.config import Config
from pymedia.models.gif_pipeline import GifPipeline
from pymedia.models.media import Media, Video
from pymedia.models.state import State
from pymedia.models.video_pipeline import VideoPipeline

from utils.factories import make_config


def _make_arguments(**kwargs) -> Arguments:
    defaults = {
        "command": CommandName.ENCODE,
        "inputs": [Path("a.mp4")],
        "crop": None,
        "debug": False,
        "end_point": None,
        "fps": None,
        "gyrate": None,
        "output": None,
        "output_on_conflict": OutputOnConflictMode.FAIL,
        "remux": False,
        "scale": None,
        "start_point": None,
        "trim_points": None,
    }
    defaults.update(kwargs)
    return Arguments(**defaults)


def _make_state() -> State:
    return State(config=make_config())


class TestStateDefaults:
    def test_default_values(self):
        state = _make_state()

        assert state.arguments is None
        assert state.inputs == []
        assert state.media == []
        assert state.output is None
        assert state.output_on_conflict is None
        assert state.video_pipeline is None
        assert state.gif_pipeline is None


class TestSetArguments:
    def test_sets_arguments(self):
        state = _make_state()
        args = _make_arguments()

        state.set_arguments(args)

        assert state.arguments is args


class TestSetInputs:
    def test_valid_inputs(self):
        state = _make_state()

        state.set_inputs([Path("a.mp4"), Path("b.mkv")])

        assert state.inputs == [Path("a.mp4"), Path("b.mkv")]

    def test_invalid_extension_raises(self):
        state = _make_state()

        with pytest.raises(InvalidVideoExtensionError):
            state.set_inputs([Path("video.txt")])


class TestSetMedia:
    def test_valid_media(self, monkeypatch):
        state = _make_state()
        fake_media = Media(duration=60.0)
        monkeypatch.setattr("pymedia.models.state.Media.load", lambda p: fake_media)

        state.set_media([Path("a.mp4"), Path("b.mp4")])

        assert state.media == [fake_media, fake_media]

    def test_missing_media_raises(self, monkeypatch):
        state = _make_state()
        monkeypatch.setattr(
            "pymedia.models.state.Media.load",
            lambda p: (_ for _ in ()).throw(FileNotFoundError()),
        )

        with pytest.raises(MissingMediaError):
            state.set_media([Path("missing.mp4")])


class TestSetOutput:
    def test_without_requires_encode(self, monkeypatch):
        state = _make_state()
        monkeypatch.setattr(
            "pymedia.services.basename_service.process_output",
            lambda output, command, **kwargs: output,
        )
        state.set_arguments(_make_arguments())
        state.media = [Media(video=Video(codec="h264"))]

        state.set_output(Path("out.mp4"))

        assert state.output == Path("out.mp4")

    def test_with_requires_encode(self, monkeypatch):
        state = _make_state()
        state.set_arguments(_make_arguments())
        state.video_pipeline = VideoPipeline(scale=["scale=-2:720"])
        monkeypatch.setattr(
            "pymedia.services.basename_service.process_output",
            lambda output, command, **kwargs: output,
        )

        state.set_output(Path("out.mkv"))

        assert state.output == Path("out.mkv")


class TestSetOutputOnConflict:
    def test_sets_from_arguments(self):
        state = _make_state()
        state.set_arguments(
            _make_arguments(output_on_conflict=OutputOnConflictMode.REPLACE)
        )

        state.set_output_on_conflict()

        assert state.output_on_conflict == OutputOnConflictMode.REPLACE

    def test_raises_without_arguments(self):
        state = _make_state()

        with pytest.raises(MissingArgumentsError):
            state.set_output_on_conflict()


class TestSetVideoPipeline:
    def test_raises_without_arguments(self):
        state = _make_state()

        with pytest.raises(MissingArgumentsError):
            state.set_video_pipeline()

    def test_sets_pipeline(self, monkeypatch):
        state = _make_state()
        monkeypatch.setattr(
            "pymedia.services.pipeline_service.process_crop",
            lambda *a, **k: ["crop=1:1:0:0"],
        )
        monkeypatch.setattr(
            "pymedia.services.pipeline_service.process_gyrate",
            lambda *a, **k: "transpose=1",
        )
        monkeypatch.setattr(
            "pymedia.services.pipeline_service.process_scale",
            lambda *a, **k: ["scale=-2:720"],
        )
        monkeypatch.setattr(
            "pymedia.services.pipeline_service.process_trim_points",
            lambda *a, **k: "1,2",
        )
        state.media = [Media(duration=10.0)]
        state.set_arguments(
            _make_arguments(
                crop="1,1,0,0",
                gyrate=90,
                scale=720,
                trim_points="0:01,0:02",
                remux=True,
            )
        )

        state.set_video_pipeline()

        assert state.video_pipeline is not None
        assert state.video_pipeline.crop == ["crop=1:1:0:0"]
        assert state.video_pipeline.gyrate == "transpose=1"
        assert state.video_pipeline.remux is True
        assert state.video_pipeline.scale == ["scale=-2:720"]
        assert state.video_pipeline.trim_points == "1,2"


class TestSetGifPipeline:
    def test_raises_without_arguments(self):
        state = _make_state()

        with pytest.raises(MissingArgumentsError):
            state.set_gif_pipeline()

    def test_sets_pipeline(self, monkeypatch):
        state = _make_state()
        monkeypatch.setattr(
            "pymedia.services.pipeline_service.process_crop",
            lambda *a, **k: ["crop=1:1:0:0"],
        )
        monkeypatch.setattr(
            "pymedia.services.pipeline_service.process_gyrate",
            lambda *a, **k: "transpose=1",
        )
        monkeypatch.setattr(
            "pymedia.services.pipeline_service.process_scale",
            lambda *a, **k: ["scale=-2:240"],
        )
        monkeypatch.setattr(
            "pymedia.services.pipeline_service.process_time",
            lambda *a, **k: 5.0,
        )
        state.media = [Media(duration=10.0)]
        state.set_arguments(
            _make_arguments(
                command=CommandName.GIF,
                crop="1,1,0,0",
                gyrate=90,
                scale=240,
                fps=15,
                start_point="0:05",
                end_point="0:10",
            )
        )

        state.set_gif_pipeline()

        assert state.gif_pipeline is not None
        assert state.gif_pipeline.crop == ["crop=1:1:0:0"]
        assert state.gif_pipeline.gyrate == "transpose=1"
        assert state.gif_pipeline.scale == ["scale=-2:240"]
        assert state.gif_pipeline.fps == 15
        assert state.gif_pipeline.start_point == 5.0
        assert state.gif_pipeline.end_point == 5.0