"""Comando ``remux``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.metadata_mixin import StripMetadataMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.mixins.remux_mixin import (
    RegeneratePtsMixin,
    RotateMetadataMixin,
    SortTracksMixin,
)
from pymedia.types import OverwriteMode, RotateMetadataMode


@dataclass(kw_only=True)
class RemuxParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    RegeneratePtsMixin,
    SortTracksMixin,
    RotateMetadataMixin,
    StripMetadataMixin,
):
    """Parámetros utilizados por el comando Remux."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        media_output: Path,
        regenerate_pts: bool,
        sort_tracks: bool,
        rotate_metadata: RotateMetadataMode,
        strip_metadata: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            media_output: Ruta absoluta del fichero de salida procesado.
            regenerate_pts: Regenera los marcadores de tiempo corruptos.
            sort_tracks: Ordena las pistas por tipo e idioma.
            rotate_metadata: Gira la imagen a través de metadatos.
            strip_metadata: No copiar los metadatos del fichero de entrada.

        Returns:
            Parámetros procesados y validados para el comando remux.
        """
        params = cls(
            overwrite=overwrite,
            regenerate_pts=regenerate_pts,
            sort_tracks=sort_tracks,
            rotate_metadata=rotate_metadata,
            strip_metadata=strip_metadata,
        )

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_media_output(
            extension=params.config.default_containers.media,
            output=media_output,
            remux=True,
        )

        return params
