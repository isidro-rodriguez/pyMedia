"""Tests para el comando de alto nivel encode (pymedia.commands.encode_command).

`encode_cmd`, `initialize_command`, `resolve_output_conflict` y `run_ffmpeg` se
mockean: esta suite comprueba la orquestación de `encode_command`, no la lógica
que ya cubren `test_ffmpeg_encode.py` y `test_command_service.py`.
"""

from pathlib import Path

import pytest
from utils.factories import make_config, make_media, reset_state

from pymedia.commands.encode_command import encode_command
from pymedia.errors import CommandGenerationError
from pymedia.models.arguments import Arguments, CommandName


def _setup_state(*, inputs, media, output=None, default_container=".mp4"):
    state = reset_state(config=make_config(default_container=default_container))
    state.inputs = inputs
    state.media = media
    state.output = output
    return state


@pytest.fixture(autouse=True)
def _patch_collaborators(monkeypatch):
    """Evita tocar disco/ffmpeg: cada test sobreescribe lo que necesite espiar."""
    monkeypatch.setattr(
        "pymedia.commands.encode_command.initialize_command", lambda args: None
    )
    monkeypatch.setattr(
        "pymedia.commands.encode_command.resolve_output_conflict",
        lambda output, logger: output,
    )
    monkeypatch.setattr(
        "pymedia.commands.encode_command.run_ffmpeg", lambda **kwargs: None
    )
    monkeypatch.setattr(
        "pymedia.commands.encode_command.encode_cmd",
        lambda input_single, output: ["ffmpeg", "-i", str(input_single)],
    )


class TestEncodeCommandInitialization:
    def test_calls_initialize_command_when_no_output(self, monkeypatch):
        _setup_state(inputs=[Path("a.mp4")], media=[make_media()])
        called = {}
        monkeypatch.setattr(
            "pymedia.commands.encode_command.initialize_command",
            lambda args: called.setdefault("args", args),
        )

        args = Arguments(command=CommandName.ENCODE, inputs=[Path("a.mp4")])
        encode_command(args)

        assert called["args"] is args

    def test_split_mode_skips_initialize_and_sets_pipeline(self, monkeypatch, tmp_path):
        state = _setup_state(inputs=[Path("a.mp4")], media=[make_media()])
        state.arguments = Arguments(command=CommandName.SPLIT, inputs=[Path("a.mp4")])

        initialize_called = []
        monkeypatch.setattr(
            "pymedia.commands.encode_command.initialize_command",
            lambda args: initialize_called.append(args),
        )
        pipeline_called = []
        monkeypatch.setattr(
            state, "set_video_pipeline", lambda: pipeline_called.append(True)
        )

        output = tmp_path / "part.mp4"
        encode_command(state.arguments, output=output)

        assert initialize_called == []
        assert pipeline_called == [True]
        assert state.output == output


class TestEncodeCommandOutputNaming:
    def test_default_output_uses_stem_and_container(self, monkeypatch, tmp_path):
        _setup_state(
            inputs=[tmp_path / "clip.mov"],
            media=[make_media()],
            default_container=".mkv",
        )
        captured = {}
        monkeypatch.setattr(
            "pymedia.commands.encode_command.encode_cmd",
            lambda input_single, output: (
                captured.setdefault("output", output) or ["ffmpeg"]
            ),
        )

        encode_command(Arguments(command=CommandName.ENCODE))

        assert captured["output"] == Path("clip_encoded.mkv").absolute()

    def test_explicit_output_single_media_used_as_is(self, monkeypatch, tmp_path):
        _setup_state(
            inputs=[tmp_path / "a.mp4"],
            media=[make_media()],
            output=tmp_path / "final.mp4",
        )
        seen = {}
        monkeypatch.setattr(
            "pymedia.commands.encode_command.encode_cmd",
            lambda input_single, output: (
                seen.setdefault("output", output) or ["ffmpeg"]
            ),
        )

        encode_command(Arguments(command=CommandName.ENCODE))

        assert seen["output"] == (tmp_path / "final.mp4").absolute()

    def test_explicit_output_multiple_media_gets_indexed_suffix(
        self, monkeypatch, tmp_path
    ):
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[make_media(), make_media()],
            output=tmp_path / "final.mp4",
        )
        outputs = []
        monkeypatch.setattr(
            "pymedia.commands.encode_command.encode_cmd",
            lambda input_single, output: outputs.append(output) or ["ffmpeg"],
        )

        encode_command(Arguments(command=CommandName.ENCODE))

        assert outputs == [
            (tmp_path / "final_0.mp4").absolute(),
            (tmp_path / "final_1.mp4").absolute(),
        ]


class TestEncodeCommandConflictHandling:
    def test_skips_media_when_conflict_resolves_to_none(self, monkeypatch, tmp_path):
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[make_media()])
        monkeypatch.setattr(
            "pymedia.commands.encode_command.resolve_output_conflict",
            lambda output, logger: None,
        )
        encode_calls = []
        monkeypatch.setattr(
            "pymedia.commands.encode_command.encode_cmd",
            lambda input_single, output: encode_calls.append(output),
        )
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.encode_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        encode_command(Arguments(command=CommandName.ENCODE))

        assert encode_calls == []
        assert run_calls == []

    def test_raises_command_generation_error_when_cmd_is_none(
        self, monkeypatch, tmp_path
    ):
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[make_media()])
        monkeypatch.setattr(
            "pymedia.commands.encode_command.encode_cmd",
            lambda input_single, output: None,
        )

        with pytest.raises(CommandGenerationError):
            encode_command(Arguments(command=CommandName.ENCODE))


class TestEncodeCommandExecution:
    def test_run_ffmpeg_receives_duration_and_description(self, monkeypatch, tmp_path):
        media = make_media()
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[media])
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.encode_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        encode_command(Arguments(command=CommandName.ENCODE))

        assert len(run_calls) == 1
        assert run_calls[0]["duration"] == media.duration.total_seconds()
        assert run_calls[0]["cmd"] == ["ffmpeg", "-i", str(tmp_path / "a.mp4")]

    def test_processes_all_media_in_order(self, monkeypatch, tmp_path):
        inputs = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
        _setup_state(inputs=inputs, media=[make_media(), make_media()])
        seen_inputs = []
        monkeypatch.setattr(
            "pymedia.commands.encode_command.encode_cmd",
            lambda input_single, output: seen_inputs.append(input_single) or ["ffmpeg"],
        )

        encode_command(Arguments(command=CommandName.ENCODE))

        assert seen_inputs == inputs
