"""Comando ``info``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class InfoParameters(
    BaseParameters,
    MediaInputMixin,
):
    """Parámetros utilizados por el comando Info."""

    overwrite: OverwriteMode = OverwriteMode.NO

    @classmethod
    def load(cls, media_input: Path) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            media_input: Ruta del fichero de vídeo a procesar.

        Returns:
            Parámetros procesados y validados para el comando info.
        """
        params = cls()

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        return params
