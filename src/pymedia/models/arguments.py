from dataclasses import dataclass
from enum import Enum

from pymedia.cli_params import GyrateMode, ScaleGifMode, ScaleMode


class CommandName(str, Enum):
    """Nombres de los comandos disponibles en la CLI."""

    TUI = "tui"
    CONCAT = "concat"
    ENCODE = "encode"
    SPLIT = "split"
    GIF = "gif"


@dataclass
class Arguments:
    command: CommandName
    crop: str | None = None
    end_point: str | None = None
    fps: int | None = None
    gyrate: GyrateMode | None = None
    output_name: str | None = None
    remux: bool = False
    scale: ScaleMode | ScaleGifMode | None = None
    start_point: str | None = None
    trim_points: str | None = None
