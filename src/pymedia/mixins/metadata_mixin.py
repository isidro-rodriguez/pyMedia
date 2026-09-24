"""Mixin para el manejo de metadatos de streams."""

from dataclasses import dataclass

from pymedia.types import RotateMetadataMode


@dataclass(kw_only=True)
class StripMetadataMixin:
    """Mixin para la borrado de  por metadatos."""

    rotate_metadata: RotateMetadataMode

    def to_rotate_metadata_cmd(self) -> list[str]:
        """Devuelve los argumentos que provocan el giro de la imagen por metadatos.

        Returns:
            Argumentos `-metadata:s:v rotate=*` para el consumo de ffmpeg.
        """
        return ["-metadata:s:v", f"rotate={self.rotate_metadata.value}"]
