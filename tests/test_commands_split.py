"""Tests para el comando de alto nivel split (pymedia.commands.split_command).

`split_cmd`, `initialize_command`, `resolve_output_conflict`, `run_ffmpeg` y
`encode_command` se mockean: esta suite comprueba la orquestación de
`split_command`, no la lógica que ya cubren `test_ffmpeg_split.py` (si existe) y
`test_services_command.py`.
"""

from pathlib import Path

import pytest
from utils.factories import make_media, reset_state

from pymedia.commands.split_command import split_command
from pymedia.errors import CommandGenerationError
from pymedia.models.arguments import Arguments, CommandName
from pymedia.models.video_pipeline import VideoPipeline


def _setup_state(*, inputs, media, output=None, pipeline=None):
    state = reset_state()
    state.inputs = inputs
    state.media = media
    state.output = output
    state.video_pipeline = pipeline or VideoPipeline()
    return state


@pytest.fixture(autouse=True)
def _patch_collaborators(monkeypatch):
    """Evita tocar disco/ffmpeg: cada test sobreescribe lo que necesite espiar."""
    monkeypatch.setattr(
        "pymedia.commands.split_command.initialize_command", lambda args: None
    )
    monkeypatch.setattr(
        "pymedia.commands.split_command.resolve_output_conflict",
        lambda output, logger: output,
    )
    monkeypatch.setattr(
        "pymedia.commands.split_command.run_ffmpeg", lambda **kwargs: None
    )
    monkeypatch.setattr(
        "pymedia.commands.split_command.split_cmd",
        lambda input_single, output: ["ffmpeg", "-i", str(input_single)],
    )
    monkeypatch.setattr(
        "pymedia.commands.split_command.encode_command", lambda args, output: None
    )


class TestSplitCommandInitialization:
    def test_calls_initialize_command(self, monkeypatch):
        _setup_state(inputs=[Path("a.mp4")], media=[make_media()])
        called = {}
        monkeypatch.setattr(
            "pymedia.commands.split_command.initialize_command",
            lambda args: called.setdefault("args", args),
        )

        args = Arguments(command=CommandName.SPLIT, inputs=[Path("a.mp4")])
        split_command(args)

        assert called["args"] is args


class TestSplitCommandOutputNaming:
    def test_default_output_uses_input_name(self, monkeypatch, tmp_path):
        _setup_state(inputs=[tmp_path / "clip.mp4"], media=[make_media()])
        captured = {}
        monkeypatch.setattr(
            "pymedia.commands.split_command.split_cmd",
            lambda input_single, output: (
                captured.setdefault("output", output) or ["ffmpeg"]
            ),
        )

        split_command(Arguments(command=CommandName.SPLIT))

        assert captured["output"] == Path("clip.mp4")

    def test_explicit_output_used_as_is(self, monkeypatch, tmp_path):
        _setup_state(
            inputs=[tmp_path / "clip.mp4"],
            media=[make_media()],
            output=tmp_path / "final.mp4",
        )
        captured = {}
        monkeypatch.setattr(
            "pymedia.commands.split_command.split_cmd",
            lambda input_single, output: (
                captured.setdefault("output", output) or ["ffmpeg"]
            ),
        )

        split_command(Arguments(command=CommandName.SPLIT))

        assert captured["output"] == (tmp_path / "final.mp4")


class TestSplitCommandConflictHandling:
    def test_returns_early_when_conflict_resolves_to_none(self, monkeypatch, tmp_path):
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[make_media()])
        monkeypatch.setattr(
            "pymedia.commands.split_command.resolve_output_conflict",
            lambda output, logger: None,
        )
        split_calls = []
        monkeypatch.setattr(
            "pymedia.commands.split_command.split_cmd",
            lambda input_single, output: split_calls.append(output),
        )
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.split_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        split_command(Arguments(command=CommandName.SPLIT))

        assert split_calls == []
        assert run_calls == []


class TestSplitCommandExecution:
    def test_run_ffmpeg_receives_duration_and_cmd(self, monkeypatch, tmp_path):
        media = make_media()
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[media])
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.split_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        split_command(Arguments(command=CommandName.SPLIT))

        assert len(run_calls) == 1
        assert run_calls[0]["duration"] == media.duration.total_seconds()
        assert run_calls[0]["cmd"] == ["ffmpeg", "-i", str(tmp_path / "a.mp4")]

    def test_uses_first_input_when_no_encode(self, monkeypatch, tmp_path):
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[make_media()],
        )
        seen_inputs = []
        monkeypatch.setattr(
            "pymedia.commands.split_command.split_cmd",
            lambda input_single, output: seen_inputs.append(input_single) or ["ffmpeg"],
        )

        split_command(Arguments(command=CommandName.SPLIT))

        assert seen_inputs == [tmp_path / "a.mp4"]

    def test_encode_required_calls_encode_command(self, monkeypatch, tmp_path):
        pipeline = VideoPipeline(crop=["crop=100:100:0:0"])
        _setup_state(
            inputs=[tmp_path / "a.mp4"],
            media=[make_media()],
            pipeline=pipeline,
        )
        encode_calls = []
        monkeypatch.setattr(
            "pymedia.commands.split_command.encode_command",
            lambda args, output: encode_calls.append(output),
        )
        split_calls = []
        monkeypatch.setattr(
            "pymedia.commands.split_command.split_cmd",
            lambda input_single, output: (
                split_calls.append((input_single, output)) or ["ffmpeg"]
            ),
        )

        split_command(Arguments(command=CommandName.SPLIT))

        assert len(encode_calls) == 1
        assert encode_calls[0].name == "a_tmp.mp4"
        assert len(split_calls) == 1
        # _split is called with the temp path and the resolved output
        assert split_calls[0][1] == Path("a.mp4")
        assert split_calls[0][0].name == "a_tmp.mp4"

    def test_raises_command_generation_error_when_cmd_is_none(
        self, monkeypatch, tmp_path
    ):
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[make_media()])
        monkeypatch.setattr(
            "pymedia.commands.split_command.split_cmd",
            lambda input_single, output: None,
        )

        with pytest.raises(CommandGenerationError):
            split_command(Arguments(command=CommandName.SPLIT))
