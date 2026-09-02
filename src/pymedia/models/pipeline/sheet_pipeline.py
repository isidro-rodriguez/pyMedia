"""Pipeline de argumentos y parámetros del subcomando sheet."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.data.types import OutputMediaType, PresetsSheetMode
from pymedia.errors import MissingParameterError
from pymedia.logger import Logger
from pymedia.models.mixins.image_mixin import ImageQualityMixin
from pymedia.models.mixins.inputs_mixin import InputSingleMixin
from pymedia.models.mixins.outputs_mixin import OutputBatchMixin
from pymedia.models.mixins.sheet_presets_mixin import SheetPresetsMixin
from pymedia.models.pipeline.base_pipeline import BaseArguments, BaseParameters


@dataclass(frozen=True, kw_only=True, slots=True)
class SheetArguments(BaseArguments):
    """Argumentos cargados por Typer para el comando Sheet.

    Attributes:
        input_list: Lista de rutas de los ficheros a procesar.
        output: Ruta del fichero de salida deseada, o None para usar la
            derivada de la entrada.
        output_directory: Directorio de salida para lotes de varios ficheros.
        overwrite: Política ante conflicto de salida ya existente. [defecto: ask]
        preset_sheet: Estilo de hoja preajustado. [defecto: HD]
    """

    input_list: list[Path]
    output_directory: Path | None
    preset_sheet: PresetsSheetMode


@dataclass(kw_only=True)
class SheetParameters(
    BaseParameters,
    InputSingleMixin,
    OutputBatchMixin,
    ImageQualityMixin,
    SheetPresetsMixin,
):
    """Parámetros utilizados por el comando Sheet.

    Attributes:
        input_single: Ruta del fichero de vídeo a procesar.
        media: Metadatos del vídeo de entrada ya resuelto y validado.
        output: Ruta absoluta del fichero de salida procesado.
        output_directory: Directorio de salida para lotes de varios ficheros.
        overwrite: Política ante conflicto de salida ya existente.
        preset_sheet: Estilo de hoja preajustado.
    """

    @classmethod
    def create(
        cls, args: SheetArguments, input_single: Path, logger: Logger
    ) -> "SheetParameters":
        """Crea y valida los parámetros del comando Sheet desde argumentos brutos.

        Args:
            args: Argumentos tipados específicos del comando.
            input_single: Ruta del fichero de vídeo a procesar.
            logger: Interfaz principal de la aplicación para generar mensajes.

        Returns:
            Instancia de SheetParameters completamente inicializada.
        """
        params = cls(overwrite=args.overwrite)
        params.create_input_single(input_single=input_single, logger=logger)
        if params.input_single is None:
            raise MissingParameterError(name="input_single")
        if params.media is None:
            raise MissingParameterError(name="media")
        params.create_output(
            input_single=params.input_single,
            input_counter=len(args.input_list),
            media=params.media,
            output_directory=args.output_directory,
            media_type=OutputMediaType.IMAGE,
            output=args.output,
            affix="_sheet",
            extension=".jpg",
        )
        params.create_preset_sheet(preset=args.preset_sheet)
        return params
