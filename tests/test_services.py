"""Tests de los servicios auxiliares de Typer (`pymedia.typer.service`).

Cubre la validación de opciones de salida en conflicto que se realizaba
antes en `OutputBatchMixin` y ahora vive en la capa de servicio.
"""

from pathlib import Path

import pytest

from pymedia.errors import ExclusiveOptionsError, OptionError
from pymedia.typer.service import validate_conflict_output_options


def test_output_and_directory_are_exclusive(tmp_path: Path) -> None:
    """Combinar `output` y `output_directory` lanza `ExclusiveOptionsError`."""
    with pytest.raises(ExclusiveOptionsError):
        validate_conflict_output_options(
            media_input_list=[Path("a.mp4")],
            output=tmp_path / "o.gif",
            output_directory=tmp_path / "dir",
        )


def test_output_with_multiple_inputs_is_rejected(tmp_path: Path) -> None:
    """Una salida explícita con varias entradas lanza `OptionError`."""
    with pytest.raises(OptionError):
        validate_conflict_output_options(
            media_input_list=[Path("a.mp4"), Path("b.mp4")],
            output=tmp_path / "o.gif",
            output_directory=None,
        )
