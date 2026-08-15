"""Tests para el comando de alto nivel concat (pymedia.commands.concat_command).

`concat_demux_cmd`, `concat_filter_cmd`, `initialize_command`,
`resolve_output_conflict` y `run_ffmpeg` se mockean: esta suite comprueba la
orquestación de `concat_command`, no la lógica que ya cubren
`test_ffmpeg_concat_demux.py` y `test_ffmpeg_concat_filter.py` (si existen).
"""

from datetime import timedelta
from pathlib import Path

import pytest
from utils.factories import make_audio, make_media, make_video, reset_state

from pymedia.commands.concat_command import concat_command
from pymedia.errors import CommandGenerationError, IncompatibleFilesError
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
        "pymedia.commands.concat_command.initialize_command", lambda args: None
    )
    monkeypatch.setattr(
        "pymedia.commands.concat_command.resolve_output_conflict",
        lambda output, logger: output,
    )
    monkeypatch.setattr(
        "pymedia.commands.concat_command.run_ffmpeg", lambda **kwargs: None
    )
    monkeypatch.setattr(
        "pymedia.commands.concat_command.concat_demux_cmd",
        lambda list_txt: ["ffmpeg", "-f", "concat", "-i", str(list_txt)],
    )
    monkeypatch.setattr(
        "pymedia.commands.concat_command.concat_filter_cmd",
        lambda: ["ffmpeg", "-filter_complex", "concat"],
    )


class TestConcatCommandInitialization:
    def test_calls_initialize_command(self, monkeypatch):
        _setup_state(inputs=[Path("a.mp4")], media=[make_media()])
        called = {}
        monkeypatch.setattr(
            "pymedia.commands.concat_command.initialize_command",
            lambda args: called.setdefault("args", args),
        )

        args = Arguments(command=CommandName.CONCAT, inputs=[Path("a.mp4")])
        concat_command(args)

        assert called["args"] is args


class TestConcatCommandOutputNaming:
    def test_default_output_uses_stem_concat_suffix(self, monkeypatch, tmp_path):
        state = _setup_state(inputs=[tmp_path / "clip.mp4"], media=[make_media()])

        concat_command(Arguments(command=CommandName.CONCAT))

        assert state.output == Path("clip_concat.mp4")

    def test_explicit_output_used_as_is(self, monkeypatch, tmp_path):
        state = _setup_state(
            inputs=[tmp_path / "clip.mp4"],
            media=[make_media()],
            output=tmp_path / "final.mp4",
        )

        concat_command(Arguments(command=CommandName.CONCAT))

        assert state.output == (tmp_path / "final.mp4")


class TestConcatCommandConflictHandling:
    def test_returns_early_when_conflict_resolves_to_none(
        self, monkeypatch, tmp_path
    ):
        _setup_state(inputs=[tmp_path / "a.mp4"], media=[make_media()])
        monkeypatch.setattr(
            "pymedia.commands.concat_command.resolve_output_conflict",
            lambda output, logger: None,
        )
        demux_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_demux_cmd",
            lambda list_txt: demux_calls.append(list_txt),
        )
        filter_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_filter_cmd",
            lambda: filter_calls.append(True),
        )
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        concat_command(Arguments(command=CommandName.CONCAT))

        assert demux_calls == []
        assert filter_calls == []
        assert run_calls == []


class TestConcatCommandCompatibility:
    def test_raises_incompatible_files_error_when_mixed_audio(
        self, monkeypatch, tmp_path
    ):
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[make_media(audio=make_audio()), make_media()],
        )

        with pytest.raises(IncompatibleFilesError):
            concat_command(Arguments(command=CommandName.CONCAT))


class TestConcatCommandExecution:
    def test_uses_concat_demux_when_compatible_and_no_encode(
        self, monkeypatch, tmp_path
    ):
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[make_media(), make_media()],
        )
        demux_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_demux_cmd",
            lambda list_txt: demux_calls.append(list_txt) or ["ffmpeg"],
        )
        filter_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_filter_cmd",
            lambda: filter_calls.append(True) or ["ffmpeg"],
        )

        concat_command(Arguments(command=CommandName.CONCAT))

        assert len(demux_calls) == 1
        assert filter_calls == []

    def test_uses_concat_filter_when_incompatible(self, monkeypatch, tmp_path):
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[make_media(video=make_video()), make_media()],
        )
        demux_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_demux_cmd",
            lambda list_txt: demux_calls.append(list_txt) or ["ffmpeg"],
        )
        filter_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_filter_cmd",
            lambda: filter_calls.append(True) or ["ffmpeg"],
        )

        concat_command(Arguments(command=CommandName.CONCAT))

        assert demux_calls == []
        assert len(filter_calls) == 1

    def test_uses_concat_filter_when_requires_encode(
        self, monkeypatch, tmp_path
    ):
        pipeline = VideoPipeline(crop=["crop=100:100:0:0"])
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[make_media(), make_media()],
            pipeline=pipeline,
        )
        demux_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_demux_cmd",
            lambda list_txt: demux_calls.append(list_txt) or ["ffmpeg"],
        )
        filter_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_filter_cmd",
            lambda: filter_calls.append(True) or ["ffmpeg"],
        )

        concat_command(Arguments(command=CommandName.CONCAT))

        assert demux_calls == []
        assert len(filter_calls) == 1

    def test_demux_writes_list_txt_with_input_paths(self, monkeypatch, tmp_path):
        inputs = [tmp_path / "a.mp4", tmp_path / "b.mp4"]
        _setup_state(inputs=inputs, media=[make_media(), make_media()])
        captured = {}

        def capture_list_txt(list_txt):
            # Read the file inside the mock while the temp dir still exists
            captured["content"] = list_txt.read_text(encoding="utf-8")
            return ["ffmpeg"]

        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_demux_cmd",
            capture_list_txt,
        )

        concat_command(Arguments(command=CommandName.CONCAT))

        expected = "\n".join(
            f"file '{p.resolve().as_posix()}'" for p in inputs
        ) + "\n"
        assert captured["content"] == expected

    def test_run_ffmpeg_receives_duration_and_cmd(self, monkeypatch, tmp_path):
        media = [make_media(), make_media()]
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=media,
        )
        demux_cmd = ["ffmpeg", "-f", "concat", "-i", "list.txt"]
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_demux_cmd",
            lambda list_txt: demux_cmd,
        )
        run_calls = []
        monkeypatch.setattr(
            "pymedia.commands.concat_command.run_ffmpeg",
            lambda **kwargs: run_calls.append(kwargs),
        )

        concat_command(Arguments(command=CommandName.CONCAT))

        assert len(run_calls) == 1
        expected_duration = (
            sum((m.duration for m in media), timedelta())
            / timedelta(milliseconds=1)
        )
        assert run_calls[0]["duration"] == expected_duration
        assert run_calls[0]["cmd"] == demux_cmd

    def test_raises_command_generation_error_when_demux_cmd_is_none(
        self, monkeypatch, tmp_path
    ):
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[make_media(), make_media()],
        )
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_demux_cmd",
            lambda list_txt: None,
        )

        with pytest.raises(CommandGenerationError):
            concat_command(Arguments(command=CommandName.CONCAT))

    def test_raises_command_generation_error_when_filter_cmd_is_none(
        self, monkeypatch, tmp_path
    ):
        _setup_state(
            inputs=[tmp_path / "a.mp4", tmp_path / "b.mp4"],
            media=[make_media(video=make_video()), make_media()],
        )
        monkeypatch.setattr(
            "pymedia.commands.concat_command.concat_filter_cmd",
            lambda: None,
        )

        with pytest.raises(CommandGenerationError):
            concat_command(Arguments(command=CommandName.CONCAT))
