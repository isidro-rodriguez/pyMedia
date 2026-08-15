"""Tests para el comando de alto nivel gif (pymedia.commands.gif_command).

`gif_cmd`, `initialize_command`, `resolve_output_conflict` y `run_ffmpeg` se
mockean: esta suite comprueba la orquestación de `gif_command`, no la lógica
que ya cubren `test_ffmpeg_gif.py` (si existe) y `test_command_service.py`.
"""

from pathlib import Path

import pytest
from utils.factories import make_media, reset_state

from pymedia.commands.gif_command import gif_command
from pymedia.errors import CommandGenerationError
from pymedia.models.arguments import Arguments, CommandName


def _setup_state(*, inputs, media, output=None):
    state = reset_state()
    state.inputs = inputs
    state.media = media
    state.output = output
    return state


@pytest.fixture(autouse=True)
def _patch_collaborators(monkeypatch):
    """Evita tocar disco/ffmpeg: cada test sobreescribe lo que necesite espiar."""
    monkeypatch.setattr(
        "pymedia.commands.gif_command.initialize_command", lambda args: None
    )
    monkeypatch.setattr(
        "pymedia.commands.gif_command.resolve_output_conflict",
        lambda output, logger: output,
    )
    monkeypatch.setattr(
        "pymedia.commands.gif_command.run_ffmpeg", lambda **kwargs: None
    )
    monkeypatch.setattr(
        "pymedia.commands.gif_command.gif_cmd",
        lambda output: ["ffmpeg", "-i", "in.mp4", str(output)],
    )


class TestGifCommandInitialization:
    def test_calls_initialize_command(self, monkeypatch):
        _setup_state(inputs=[Path("a.mp4")], media=[make_media()])
        called = {}
        monkeypatch.setattr(
            "pymedia.commands.gif_command.initialize_command",
            lambda args: called.setdefault("args", args),
        )

        args = Arguments(command=CommandName.GIF, inputs=[Path("a.mp4")])
        gif_command(args)

        assert called["args"] is args


class TestGifCommandOutputNaming:
    def test_default_output_uses_input_stem_and_gif_extension(
        self, monkeypatch, tmp_path
    ):
        _setup_state(inputs=[tmp_path / "clip.mp4"], media=[make_media()])
        captured = {}
        monkeypatch.setattr(
            "pymedia.commands.gif_command.gif_cmd",
            lambda output: captured.setdefault("output", output) or ["ffmpeg"],
        )

        gif_command(Arguments(command=CommandName.GIF))

        assert captured["output"] == Path("clip.gif").absolute()

    def test_explicit_output_used_as_is(self, monkeypatch, tmp_path):
        _setup_state(
            inputs=[tmp_path / "clip.mp4"],
            media=[make_media()],
            output=tmp_path / "final.gif",
        )
        captured = {}
        monkeypatch.setattr(
            "pymedia.commands.gif_command.gif_cmd",
            lambda output: captured.setdefault("output", output) or ["ffmpeg"],
        )

        gif_command(Arguments(command=CommandName.GIF))

        assert captured["output"] == (tmp_path / "final.gif").absolute()


class TestGifCommandConflictHandling:
    def test_returns_early_when_conflict_resolves_to_none(self, monkeypatch, tmp_path):
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[make_media()])
        monkeypatch.setattr(
            "pymedia.commands.gif_command.resolve_output_conflict",
            lambda output, logger: None,
        )
        gif_calls = []
        monkeypatch.setattr(
            "pymedia.commands.gif_command.gif_cmd",
            lambda output: gif_calls.append(output),
        )
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.gif_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        gif_command(Arguments(command=CommandName.GIF))

        assert gif_calls == []
        assert run_calls == []

    def test_raises_command_generation_error_when_cmd_is_none(
        self, monkeypatch, tmp_path
    ):
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[make_media()])
        monkeypatch.setattr("pymedia.commands.gif_command.gif_cmd", lambda output: None)

        with pytest.raises(CommandGenerationError):
            gif_command(Arguments(command=CommandName.GIF))


class TestGifCommandExecution:
    def test_run_ffmpeg_receives_duration_of_first_media_and_cmd(
        self, monkeypatch, tmp_path
    ):
        media = make_media()
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[media])
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.gif_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        gif_command(Arguments(command=CommandName.GIF))

        assert len(run_calls) == 1
        assert run_calls[0]["duration"] == media.duration.total_seconds()
        assert run_calls[0]["cmd"] == [
            "ffmpeg",
            "-i",
            "in.mp4",
            str(Path("a.gif").absolute()),
        ]

    def test_uses_first_input_and_first_media_only(self, monkeypatch, tmp_path):
        """gif_command siempre opera sobre state.inputs[0] / state.media[0],
        aunque haya más de un input en state (a diferencia de encode/split)."""
        first_media = make_media()
        second_media = make_media()
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[first_media, second_media],
        )
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.gif_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        gif_command(Arguments(command=CommandName.GIF))

        assert len(run_calls) == 1
        assert run_calls[0]["duration"] == first_media.duration.total_seconds()
