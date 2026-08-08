from dataclasses import dataclass

from pymedia.logger import get_logger

logger = get_logger("pipeline")


@dataclass
class VideoPipeline:
    crop: list[str | None] | None = None
    gyrate: str | None = None
    remux: bool = False
    scale: list[int | None] | None = None
    trim_points: str | None = None

    @classmethod
    def load(cls) -> "VideoPipeline":
        """Crea un pipeline desde los parámetros CLI, convirtiendo enums a valores."""
        return cls()

    @property
    def has_operations(self) -> bool:
        """True si hay al menos una operación activa en el pipeline."""
        return any(
            field is not None
            for field in (
                self.crop,
                self.gyrate,
                self.remux,
                self.scale,
                self.trim_points,
            )
        )

    @property
    def requires_encode(self) -> bool:
        """True si hay al menos una operación que requiera transcodificación."""
        return any(
            field is not None
            for field in (
                self.crop,
                self.gyrate,
                self.remux,
                self.scale,
            )
        )
