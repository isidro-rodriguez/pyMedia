from dataclasses import dataclass
from pathlib import Path

from pymedia.typer_options import (
    GyrateMode,
    OutputOnConflictMode,
    ScaleGifMode,
    ScaleVideoMode,
)


@dataclass
class Arguments:
    output_on_conflict: OutputOnConflictMode
    crop: str | None = None
    debug: bool = False
    end_point: str | None = None
    fps: int | None = None
    gyrate: GyrateMode | None = None
    input_single: Path | None = None
    inputs: list[Path] | None = None
    output: Path | None = None
    remux: bool = False
    scale: ScaleVideoMode | ScaleGifMode | None = None
    start_point: str | None = None
    trim_points: str | None = None
