from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from pymedia.cli_params import (
    GyrateMode,
    OutputOnConflictMode,
    ScaleGifMode,
    ScaleVideoMode,
)


class CommandName(StrEnum):
    """Nombres de los comandos disponibles en la CLI."""

    CONCAT = "concat"
    ENCODE = "encode"
    SPLIT = "split"
    GIF = "gif"


@dataclass
class Arguments:
    # Required arguments
    command: CommandName
    inputs: list[Path] | None = None
    trim_points: str | None = None
    # Optional arguments
    crop: str | None = None
    end_point: str | None = None
    fps: int | None = None
    gyrate: GyrateMode | None = None
    output: Path | None = None
    output_on_conflict: OutputOnConflictMode | None = None
    remux: bool = False
    scale: ScaleVideoMode | ScaleGifMode | None = None
    start_point: str | None = None
