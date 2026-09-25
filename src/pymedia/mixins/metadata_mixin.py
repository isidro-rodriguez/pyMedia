"""Mixin para el manejo de metadatos de streams."""

from dataclasses import dataclass


@dataclass(kw_only=True)
class StripMetadataMixin:
    """Mixin para indicar que no se copian metadatos de fichero origen."""

    strip_metadata: bool = False

    @staticmethod
    def to_strip_metadata_cmd() -> list[str]:
        """Devuelve los argumentos que provocan que no se copie metadatos del origen.

        Returns:
            Argumentos para función ffmpeg para no copiar metadatos del origen.
        """
        return ["-map_metadata", "-1"]
