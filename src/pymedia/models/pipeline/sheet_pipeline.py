from dataclasses import dataclass
from pathlib import Path

from pymedia.errors import MissingParameterError
from pymedia.logger import Logger
from pymedia.models.enums import OutputMediaType, OverwriteMode, PresetsSheetMode
from pymedia.models.mixins.inputs_mixin import InputSingleMixin
from pymedia.models.mixins.outputs_mixin import OutputBatchMixin
from pymedia.models.mixins.sheet_presets_mixin import SheetPresetsMixin


@dataclass(frozen=True, kw_only=True, slots=True)
class SheetArguments:
    """Argumentos cargados por Typer para el comando Sheet.

    Attributes:
        input_list: Lista de rutas de los vídeos a procesar.
        output: Ruta del fichero de salida. [defecto: INPUT_SINGLE_sheet.jpg]
        output_directory: Directorio de salida para lotes de varios ficheros.
        overwrite: Indica actuación ante fichero de salida ya existente. [defecto: ask]
        preset_sheet: Indica el estilo de hoja preajustado. [default: HD]
    """

    input_list: list[Path]
    output: Path | None
    output_directory: Path | None
    overwrite: OverwriteMode
    preset_sheet: PresetsSheetMode


@dataclass(kw_only=True)
class SheetParameters(InputSingleMixin, OutputBatchMixin, SheetPresetsMixin):
    """Parámetros utilizados por el comando Sheet.

    Attributes:
        input_single: Rutas del vídeo a procesar.
        media: Metadatos del vídeo de entrada ya resuelto y validado.
        output: Ruta del fichero de salida procesada, válida solo cuando
            el lote contiene un único fichero.
        output_directory: Directorio de salida para lotes de varios ficheros.
        overwrite: Indica actuación ante fichero de salida ya existente. [defecto: ask]
        preset_sheet: Estilo de hoja preajustado.
    """

    overwrite: OverwriteMode

    @classmethod
    def create(
        cls, args: SheetArguments, input_single: Path, logger: Logger
    ) -> "SheetParameters":
        """Crea y valida los parámetros del comando Sheet desde argumentos brutos.

        Args:
            args: Argumentos crudos recibidos desde la CLI.
            input_single: Rutas del vídeo a procesar.
            logger: Logger para trazas de progreso.

        Returns:
            Instancia de SheetParameters completamente inicializada.
        """

        params = cls(overwrite=args.overwrite)
        params.create_input_single(input_single=input_single, logger=logger)
        if params.input_single is None:
            raise MissingParameterError(name="input_single")
        if params.media is None:
            raise MissingParameterError(name="media")
        params.create_output_batch(
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
