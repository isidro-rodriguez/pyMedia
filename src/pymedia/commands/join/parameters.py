"""Comando ``join``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.media_mixin import MediaListMixin
from pymedia.mixins.metadata_mixin import StripMetadataMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class JoinParameters(
    BaseParameters,
    MediaListMixin,
    MediaOutputMixin,
    StripMetadataMixin,
):
    """Parámetros utilizados por el comando Join."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input_list: list[Path],
        media_output: Path | None = None,
        strip_metadata: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input_list: Lista de rutas de los ficheros de vídeo a unir.
            media_output: Ruta absoluta del fichero de salida procesado.
            strip_metadata: No copiar los metadatos del fichero de entrada.

        Returns:
            Parámetros procesados y validados para el comando join.
        """
        params = cls(overwrite=overwrite, strip_metadata=strip_metadata)

        params.create_media_list(
            media_input_list=media_input_list,
            logger=params.logger,
        )

        params.create_media_output(
            extension=params.config.default_containers.media,
            output=media_output,
            media_list=params.media_list,
            remux=True,
        )

        return params
