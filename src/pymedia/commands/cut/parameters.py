"""Comando ``cut``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.errors import MissingParameterError
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.metadata_mixin import StripMetadataMixin
from pymedia.mixins.outputs_mixin import MediaOutputMixin
from pymedia.mixins.timestamps_mixin import TimestampAtMixin, TimestampStartEndMixin
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class CutParameters(
    BaseParameters,
    MediaInputMixin,
    MediaOutputMixin,
    TimestampAtMixin,
    TimestampStartEndMixin,
    StripMetadataMixin,
):
    """Parámetros utilizados por el comando Cut."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        timestamp_at: str | None = None,
        timestamp_start: str | None = None,
        timestamp_end: str | None = None,
        media_output: Path | None = None,
        strip_metadata: bool = False,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            timestamp_at: Lista de marcas de tiempo para dividir el vídeo.
            timestamp_start: Corte inicial del vídeo de salida.
            timestamp_end: Corte final del vídeo de salida.
            media_output: Ruta absoluta del fichero de salida procesado.
            strip_metadata: No copiar los metadatos del fichero de entrada.

        Returns:
            Parámetros procesados y validados para el comando cut.

        Raises:
            MissingParameterError: Si la salida procesada no se pudo obtener.
        """
        params = cls(overwrite=overwrite, strip_metadata=strip_metadata)

        params.create_media_input(
            media_input=media_input,
            logger=params.logger,
        )

        params.create_media_output(
            extension=media_input.suffix,
            affix="_split",
            output=media_output,
            remux=True,
        )

        if timestamp_at is not None:
            if params.media_output is None:
                raise MissingParameterError(name="media_output")
            out = params.media_output.absolute()
            params.media_output = out.with_stem(f"{out.stem}_%03d")

        params.create_timestamp_at(
            times_str=timestamp_at,
        )

        params.create_timestamp_start_end(
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )

        return params
