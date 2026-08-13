from dataclasses import dataclass

from pymedia.logger import get_logger

logger = get_logger("pipeline")


@dataclass
class VideoPipeline:
    crop: list[str | None] | None = None
    gyrate: str | None = None
    remux: bool = False
    scale: list[str | None] | None = None
    trim_points: str | None = None

    @classmethod
    def load(cls) -> "VideoPipeline":
        """Crea un pipeline desde los parámetros CLI, convirtiendo enums a valores."""
        return cls()

    @property
    def requires_encode(self) -> bool:
        """True si hay al menos una operación que requiera transcodificación."""
        return (
            self.crop is not None
            or self.gyrate is not None
            or self.remux is True
            or self.scale is not None
        )
