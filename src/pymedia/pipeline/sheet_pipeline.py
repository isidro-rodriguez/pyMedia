"""Subcomando `sheet`: genera hojas de contactos con capturas de varios vídeos."""

import tempfile
from pathlib import Path

from pymedia.data.types import OverwriteMode, PresetsSheetMode
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingMediaPropertyError,
    MissingParameterError,
)
from pymedia.ffmpeg.sheet_cmd import SheetCmd
from pymedia.locales import _  # noqa
from pymedia.models.pipeline.sheet_pipeline import SheetArguments, SheetParameters
from pymedia.pipeline.base_pipeline import BasePipeline, BatchPipeline
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    InputListArgument,
    OutputDirectoryOption,
    OutputOption,
    OverwriteOption,
    PresetSheetOption,
)


class SheetCommand(BatchPipeline[SheetArguments, SheetParameters]):
    """Comando de CLI que genera una hoja de capturas con cabecera de metadatos."""

    command_name = "sheet"
    help = _("Generates a thumbnail grid sheet with media info header.")

    @staticmethod
    def cli(
        input_list: InputListArgument,
        output: OutputOption = None,
        output_directory: OutputDirectoryOption = None,
        overwrite: OverwriteOption = OverwriteMode.ASK,
        preset_sheet: PresetSheetOption = PresetsSheetMode.HD,
        debug: DebugOption = False,
        help_: HelpOption = False,
    ) -> None:
        """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

        Args:
            input_list: Lista de vídeos a procesar.
            output: Ruta de salida para un único vídeo de entrada.
            output_directory: Directorio de salida para lotes de varios vídeos.
            overwrite: Política ante un fichero de salida existente.
            preset_sheet: Estilo de hoja preajustado (FHD, HD o WEB).
            debug: Habilita el nivel de log DEBUG.
            help_: Muestra la ayuda del comando.
        """
        SheetCommand.run(
            args=BasePipeline.build_args(
                args_cls=SheetArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self, input_single: Path) -> SheetParameters:
        """Valida y parsea los argumentos en parámetros procesados para un vídeo.

        Args:
            input_single: Ruta del fichero de vídeo a procesar.

        Returns:
            Parámetros procesados y validados para el comando.
        """
        return SheetParameters.create(
            args=self.args, logger=self.logger, input_single=input_single
        )

    def process_cmd(self, params: SheetParameters) -> None:
        """Construye y ejecuta los comandos ffmpeg de capturas y cabecera.

        Args:
            params: Parámetros procesados y validados para el comando.
        """
        if params.input_single is None:
            raise MissingParameterError(name="input_single")
        if params.media is None:
            raise MissingMediaError(path=str(params.input_single))
        if params.media.duration is None:
            raise MissingMediaPropertyError(name="media.duration")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tile_tmp = Path(tmp_dir) / "tile_tmp.jpg"

            sheet_instance = SheetCmd(params=params, tile_tmp=tile_tmp)
            snapshots_cmd = sheet_instance.create_snapshots()
            header_cmd = sheet_instance.create_header()

            if snapshots_cmd is None:
                raise CommandGenerationError(name="generate_sheet_cmd")
            self.logger.debug(msg=_("FFmpeg command: %(cmd)s"), cmd=snapshots_cmd)

            if header_cmd is None:
                raise CommandGenerationError(name="generate_header_cmd")
            self.logger.debug(msg=_("FFmpeg command: %(cmd)s"), cmd=header_cmd)

            self.run_ffmpeg(
                cmd=snapshots_cmd,
                description=_("Generating sheet snapshots"),
                stall_timeout=self.config.app.stall_timeout,
                command_name=self.command_name,
                total_steps=sheet_instance.capture_count,
            )

            self.run_ffmpeg(
                cmd=header_cmd,
                description=_("Generating sheet header"),
                stall_timeout=self.config.app.stall_timeout,
                command_name=self.command_name,
            )

        self.logger.info(
            msg=_("Metadata generated successfully: %(output)s"), output=params.output
        )
