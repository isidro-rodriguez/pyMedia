"""Subcomando `sheet`: genera hojas de contactos con capturas de varios vídeos."""

import tempfile
from pathlib import Path

from pymedia.errors import (
    CommandGenerationError,
    MissingMediaPropertyError,
    MissingParameterError,
)
from pymedia.ffmpeg.sheet_cmd import SheetCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import SheetParameters
from pymedia.pipeline import BasePipeline
from pymedia.types import OverwriteMode, PresetsSheetMode


class SheetPipeline(BasePipeline[SheetParameters]):
    """Comando de CLI que genera una hoja de capturas con cabecera de metadatos."""

    def process_parameters(
        self,
        media_input: Path,
        overwrite: OverwriteMode,
        preset_sheet: PresetsSheetMode,
        output: Path | None = None,
        output_directory: Path | None = None,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados para un vídeo.

        Args:
            media_input: Ruta del fichero de vídeo a procesar.
            overwrite: Política ante conflicto de salida ya existente.
            preset_sheet: Estilo de hoja preajustado.
            output: Ruta absoluta del fichero de salida procesado.
            output_directory: Directorio de salida para lotes de ficheros.
        """
        params = SheetParameters(overwrite=overwrite)
        params.create_media_input(media_input=media_input, logger=self.logger)
        if params.media is None:
            raise MissingParameterError(name="media")
        params.create_image_output(
            output=output,
            output_directory=output_directory,
            affix="_sheet",
            extension=".jpg",
        )
        params.create_preset_sheet(preset=preset_sheet)
        self.params = params

    def process_cmd(self) -> None:
        """Construye y ejecuta los comandos ffmpeg de capturas y cabecera."""
        if self.params.media is None:
            raise MissingParameterError(name="media")
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
            output=self.params.image_output,
        )
