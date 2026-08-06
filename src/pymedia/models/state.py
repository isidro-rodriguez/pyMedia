from dataclasses import dataclass, field
from pathlib import Path

from pymedia.models.config import Config
from pymedia.models.media import Media
from pymedia.models.pipeline import Pipeline


@dataclass
class State:
    config: Config | None = None
    inputs: list[Path] = field(default_factory=list)
    output: Path | None = None
    media: list[Media] = field(default_factory=list)
    pipeline: Pipeline | None = None
