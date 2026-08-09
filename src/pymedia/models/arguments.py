from dataclasses import dataclass
from enum import Enum, StrEnum
from pathlib import Path

from pymedia.cli_params import GyrateMode, ScaleGifMode, ScaleMode


class CommandName(StrEnum):
    """Nombres de los comandos disponibles en la CLI."""

    TUI = "tui"
    CONCAT = "concat"
    ENCODE = "encode"
    SPLIT = "split"
    GIF = "gif"


@dataclass
class Arguments:
    # Default parameters
    command: CommandName
    inputs: list[Path] | Path | None = None
    trim_points: str | None = None
    # Optional parameters
    crop: str | None = None
    end_point: str | None = None
    fps: int | None = None
    gyrate: GyrateMode | None = None
    output_name: str | None = None
    remux: bool = False
    scale: ScaleMode | ScaleGifMode | None = None
    start_point: str | None = None
