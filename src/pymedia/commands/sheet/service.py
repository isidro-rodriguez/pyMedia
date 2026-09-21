"""Comando ``sheet``: service."""

import tempfile
from pathlib import Path

from pymedia.commands.base_service import BaseService
from pymedia.commands.sheet.cmd import SheetCmd
from pymedia.commands.sheet.parameters import SheetParameters
from pymedia.errors import (
    MissingParameterError,
    MissingPropertyError,
)
from pymedia.locales import _


class SheetService(BaseService[SheetParameters]):
    """Comando de CLI que genera una hoja de capturas con cabecera de metadatos."""

    def start(self) -> None:
        """Construye y ejecuta los comandos ffmpeg de capturas y cabecera.

        Raises:
            MissingParameterError: Si el medio no se pudo obtener.
            MissingPropertyError: Si falta la duración del medio o la ruta de
                imagen de salida.
            CommandGenerationError: Si no se pudo generar el comando de
                capturas o el de cabecera.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media.duration is None:
            raise MissingPropertyError(name="media.duration")
        if self.params.image_output is None:
            raise MissingPropertyError(name="image_output")

        if not self.resolve_overwrite(output_list=[self.params.image_output]):
            return

        with tempfile.TemporaryDirectory() as tmp_dir:
            tile_tmp = Path(tmp_dir) / "tile_tmp.jpg"

            sheet_instance = SheetCmd(params=self.params, tile_tmp=tile_tmp)
            snapshots_cmd = sheet_instance.create_snapshots()
            header_cmd = sheet_instance.create_header()

            self.run_ffmpeg(
                cmd=snapshots_cmd,
                description=_("Generating sheet snapshots"),
                total_steps=sheet_instance.capture_count,
                output_list=[tile_tmp],
            )

            self.run_ffmpeg(
                cmd=header_cmd,
                description=_("Generating sheet header"),
                output_list=[self.params.image_output],
            )

        self.logger.info(
            msg=_("Sheet generated successfully: %(output)s"),
            output=self.params.image_output,
        )
