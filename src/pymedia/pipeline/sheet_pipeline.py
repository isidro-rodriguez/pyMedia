"""Subcomando `sheet`: genera hojas de contactos con capturas de varios vídeos."""

import tempfile
from pathlib import Path

from pymedia.data.types import OutputMediaType, OverwriteMode, PresetsSheetMode
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingMediaPropertyError,
    MissingParameterError,
)
from pymedia.ffmpeg.sheet_cmd import SheetCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import SheetParameters
from pymedia.pipeline import BasePipeline


class SheetPipeline(BasePipeline[SheetParameters]):
    """Comando de CLI que genera una hoja de capturas con cabecera de metadatos."""

    def process_parameters(
        self,
        input_single: Path,
        overwrite: OverwriteMode,
        preset_sheet: PresetsSheetMode,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados para un vídeo.

        Args:
            input_single: Ruta del fichero de vídeo a procesar.
            overwrite: Política ante conflicto de salida ya existente.
            preset_sheet: Estilo de hoja preajustado.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de ficheros.
        """
        params = SheetParameters(overwrite=overwrite)
        params.create_input_single(input_single=input_single, logger=self.logger)
        if params.input_single is None:
            raise MissingParameterError(name="input_single")
        if params.media is None:
            raise MissingParameterError(name="media")
        params.create_output(
            input_single=params.input_single,
            media=params.media,
            output_directory=output_directory,
            media_type=OutputMediaType.IMAGE,
            output=output,
            affix="_sheet",
            extension=".jpg",
        )
        params.create_preset_sheet(preset=preset_sheet)
        self.params = params

    def process_cmd(self) -> None:
        """Construye y ejecuta los comandos ffmpeg de capturas y cabecera."""
        if self.params.input_single is None:
            raise MissingParameterError(name="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))
        if self.params.media.duration is None:
            raise MissingMediaPropertyError(name="media.duration")

        with tempfile.TemporaryDirectory() as tmp_dir:
            tile_tmp = Path(tmp_dir) / "tile_tmp.jpg"

            sheet_instance = SheetCmd(params=self.params, tile_tmp=tile_tmp)
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
                total_steps=sheet_instance.capture_count,
            )

            self.run_ffmpeg(
                cmd=header_cmd,
                description=_("Generating sheet header"),
            )

        self.logger.info(
            msg=_("Metadata generated successfully: %(output)s"),
            output=self.params.output,
        )
