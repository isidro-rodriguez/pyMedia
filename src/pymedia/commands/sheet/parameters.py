"""Comando ``sheet``: procesador de parámetros."""

from dataclasses import dataclass
from pathlib import Path
from typing import Self

from pymedia.commands.base_parameters import BaseParameters
from pymedia.errors import MissingParameterError
from pymedia.mixins.image_mixin import ImageQualityMixin
from pymedia.mixins.media_mixin import MediaInputMixin
from pymedia.mixins.outputs_mixin import ImageOutputMixin
from pymedia.mixins.sheet_presets_mixin import SheetPresetsMixin
from pymedia.types import OverwriteMode, PresetsSheetMode


@dataclass(kw_only=True)
class SheetParameters(
    BaseParameters,
    MediaInputMixin,
    ImageOutputMixin,
    ImageQualityMixin,
    SheetPresetsMixin,
):
    """Parámetros utilizados por el comando Sheet."""

    @classmethod
    def load(
        cls,
        overwrite: OverwriteMode,
        media_input: Path,
        preset_sheet: PresetsSheetMode,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> Self:
        """Valida y parsea los argumentos en parámetros procesados para un vídeo.

        Args:
            overwrite: Política de conflicto ante fichero de salida existente.
            media_input: Ruta del fichero de vídeo a procesar.
            preset_sheet: Estilo de hoja preajustado.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de ficheros.

        Returns:
            Parámetros procesados y validados para el comando sheet.

        Raises:
            MissingParameterError: Si el medio no se pudo obtener.
        """
        params = cls(overwrite=overwrite)
        params.create_media_input(media_input=media_input, logger=params.logger)
        if params.media is None:
            raise MissingParameterError(name="media")
        params.create_image_output(
            output=output,
            output_directory=output_directory,
            affix="_sheet",
            extension=params.config.default_containers.image,
        )
        params.create_preset_sheet(preset=preset_sheet)
        return params
