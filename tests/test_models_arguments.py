"""Tests para la validación del modelo Arguments (pymedia.models.arguments)."""

from pathlib import Path

import pytest

from pymedia.models.arguments import Arguments, CommandName

# -----------------------------------------------------------------------------
#  CommandName
# -----------------------------------------------------------------------------


def test_command_name_valid_values():
    """Test que CommandName acepta los valores válidos."""
    cases = [
        "concat",
        "encode",
        "split",
        "gif",
    ]
    for value in cases:
        assert CommandName(value) is not None


def test_command_name_invalid_value():
    """Test que CommandName lanza error para valores inválidos."""
    with pytest.raises(ValueError):
        CommandName("invalid")


# -----------------------------------------------------------------------------
#  Arguments
# -----------------------------------------------------------------------------


def test_arguments_minimal():
    """Test que Arguments se crea con los campos mínimos requeridos."""
    args = Arguments(command=CommandName.ENCODE)
    assert args.command == CommandName.ENCODE
    assert args.inputs is None
    assert args.trim_points is None
    assert args.crop is None
    assert args.debug is False
    assert args.end_point is None
    assert args.fps is None
    assert args.gyrate is None
    assert args.output is None
    assert args.output_on_conflict is None
    assert args.remux is False
    assert args.scale is None
    assert args.start_point is None


def test_arguments_with_all_fields():
    """Test que Arguments se crea con todos los campos poblados."""
    from pymedia.cli_params import GyrateMode
    from pymedia.models.arguments import (
        OutputOnConflictMode,
        ScaleVideoMode,
    )

    args = Arguments(
        command=CommandName.CONCAT,
        inputs=[Path("input1.mp4"), Path("input2.mp4")],
        trim_points="00:00:00-00:01:00",
        crop="1920x1080",
        debug=True,
        end_point="00:00:30",
        fps=30,
        gyrate=GyrateMode.d90,
        output=Path("output.mp4"),
        output_on_conflict=OutputOnConflictMode.REPLACE,
        remux=True,
        scale=ScaleVideoMode.P720,
        start_point="00:00:10",
    )
    assert args.command == CommandName.CONCAT
    assert args.inputs == [Path("input1.mp4"), Path("input2.mp4")]
    assert args.trim_points == "00:00:00-00:01:00"
    assert args.crop == "1920x1080"
    assert args.debug is True
    assert args.end_point == "00:00:30"
    assert args.fps == 30
    assert args.gyrate == GyrateMode.d90
    assert args.output == Path("output.mp4")
    assert args.output_on_conflict == OutputOnConflictMode.REPLACE
    assert args.remux is True
    assert args.scale == ScaleVideoMode.P720
    assert args.start_point == "00:00:10"


def test_arguments_invalid_command():
    """Test que Arguments acepta cualquier comando (es un StrEnum, no hay validación en el dataclass)."""
    # Arguments es un dataclass, no valida el comando automáticamente
    args = Arguments(command="invalid_command", inputs=[Path("test.mp4")])
    assert args.command == "invalid_command"


def test_arguments_with_inputs():
    """Test que Arguments acepta lista de inputs."""
    args = Arguments(
        command=CommandName.CONCAT, inputs=[Path("file1.mp4"), Path("file2.mp4")]
    )
    assert args.inputs == [Path("file1.mp4"), Path("file2.mp4")]


def test_arguments_optional_fields_defaults():
    """Test que los campos opcionales tienen valores por defecto correctos."""
    args = Arguments(command=CommandName.ENCODE)
    # Los booleanos por defecto son False
    assert args.debug is False
    assert args.remux is False
    # Los strings/nones por defecto son None
    assert args.inputs is None
    assert args.trim_points is None
    assert args.crop is None
    assert args.end_point is None
    assert args.fps is None
    assert args.gyrate is None
    assert args.output is None
    assert args.output_on_conflict is None
    assert args.scale is None
    assert args.start_point is None
