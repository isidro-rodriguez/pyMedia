"""Tests para el módulo principal pymedia.main."""

from pathlib import Path

import pytest
import typer
from typer.testing import CliRunner

from pymedia.cli_params import (
    GyrateMode,
    OutputOnConflictMode,
    ScaleGifMode,
    ScaleVideoMode,
    _validate_path,
    _validate_path_list,
)
from pymedia.errors import InsufficientInputError, MissingOptionsError
from pymedia.main import _build_arguments, app
from pymedia.models.arguments import Arguments, CommandName

runner = CliRunner()


# -----------------------------------------------------------------------------
#  _build_arguments()
# -----------------------------------------------------------------------------


class TestBuildArguments:
    def test_encode_arguments(self):
        local_vars = {
            "inputs": [Path("a.mp4")],
            "crop": "100,100,0,0",
            "debug": False,
            "gyrate": GyrateMode.d90,
            "help_": False,
            "output": None,
            "output_on_conflict": OutputOnConflictMode.FAIL,
            "remux": False,
            "scale": None,
        }

        args = _build_arguments(CommandName.ENCODE, local_vars)

        assert args.command is CommandName.ENCODE
        assert args.inputs == [Path("a.mp4")]
        assert args.crop == "100,100,0,0"
        assert args.gyrate is GyrateMode.d90
        assert args.output is None
        assert args.output_on_conflict is OutputOnConflictMode.FAIL
        assert args.remux is False
        assert args.scale is None

    def test_input_single_mapped_to_inputs(self):
        local_vars = {
            "input_single": Path("video.mp4"),
            "trim_points": "0:10,0:20",
            "debug": False,
            "crop": None,
            "gyrate": None,
            "help_": False,
            "output": None,
            "output_on_conflict": OutputOnConflictMode.FAIL,
            "remux": False,
            "scale": None,
        }

        args = _build_arguments(CommandName.SPLIT, local_vars)

        assert args.command is CommandName.SPLIT
        assert args.inputs == [Path("video.mp4")]
        assert args.trim_points == "0:10,0:20"

    def test_unknown_keys_ignored(self):
        local_vars = {
            "inputs": [Path("a.mp4")],
            "unknown_key": "should_be_ignored",
            "crop": None,
        }

        args = _build_arguments(CommandName.ENCODE, local_vars)

        assert args.inputs == [Path("a.mp4")]
        assert not hasattr(args, "unknown_key")


# -----------------------------------------------------------------------------
#  Validación de la CLI principal
# -----------------------------------------------------------------------------


class TestMainCallback:
    def test_help_shows_and_exits(self):
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "pyMedia" in result.output

    def test_subcommand_help_shows(self):
        result = runner.invoke(app, ["encode", "--help"])

        assert result.exit_code == 0
        assert "Encode options" in result.output


# -----------------------------------------------------------------------------
#  Validación de comandos CLI (sin ejecutar ffmpeg)
# -----------------------------------------------------------------------------


class TestCliCommands:
    def test_concat_requires_two_inputs(self, tmp_path, monkeypatch):
        f = tmp_path / "a.mp4"
        f.write_bytes(b"data")

        monkeypatch.setattr("pymedia.main.concat_command", lambda args: None)

        result = runner.invoke(app, ["concat", str(f)])

        assert result.exit_code != 0
        assert isinstance(result.exception, InsufficientInputError)

    def test_encode_requires_option(self, tmp_path, monkeypatch):
        f = tmp_path / "a.mp4"
        f.write_bytes(b"data")

        monkeypatch.setattr("pymedia.main.encode_command", lambda args: None)

        result = runner.invoke(app, ["encode", str(f)])

        assert result.exit_code != 0
        assert isinstance(result.exception, MissingOptionsError)

    def test_encode_with_crop_invokes_command(self, tmp_path, monkeypatch):
        f = tmp_path / "a.mp4"
        f.write_bytes(b"data")

        captured = {}
        monkeypatch.setattr(
            "pymedia.main.encode_command",
            lambda args: captured.update(args=args),
        )

        result = runner.invoke(app, ["encode", str(f), "--crop", "100,100,0,0"])

        assert result.exit_code == 0
        assert "args" in captured
        assert captured["args"].crop == "100,100,0,0"

    def test_gif_invokes_command(self, tmp_path, monkeypatch):
        f = tmp_path / "a.mp4"
        f.write_bytes(b"data")

        captured = {}
        monkeypatch.setattr(
            "pymedia.main.gif_command",
            lambda args: captured.update(args=args),
        )

        result = runner.invoke(app, ["gif", str(f)])

        assert result.exit_code == 0
        assert "args" in captured
        assert captured["args"].command is CommandName.GIF

    def test_split_invokes_command(self, tmp_path, monkeypatch):
        f = tmp_path / "a.mp4"
        f.write_bytes(b"data")

        captured = {}
        monkeypatch.setattr(
            "pymedia.main.split_command",
            lambda args: captured.update(args=args),
        )

        result = runner.invoke(app, ["split", str(f), "--trim-points", "00:00:00-00:01:00"])

        assert result.exit_code == 0
        assert "args" in captured
        assert captured["args"].command is CommandName.SPLIT