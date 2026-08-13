from dataclasses import dataclass

from pymedia.logger import get_logger

logger = get_logger("gif_pipeline")


@dataclass
class GifPipeline:
    crop: list[str | None] | None = None
    end_point: float | None = None
    fps: int | None = None
    gyrate: str | None = None
    scale: list[str | None] | None = None
    start_point: float | None = None

    @classmethod
    def load(cls) -> "GifPipeline":
        """Crea un pipeline desde los parámetros CLI, convirtiendo enums a valores."""
        return cls()
