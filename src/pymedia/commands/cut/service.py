"""Comando ``cut``: service."""

import sys
from pathlib import Path

from pymedia.commands.base_service import BaseService
from pymedia.commands.cut.cmd import CutCmd
from pymedia.commands.cut.parameters import CutParameters
from pymedia.errors import MissingParameterError
from pymedia.locales import translate as _


class CutService(BaseService[CutParameters]):
    """Comando de CLI para el corte de un vídeo."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la división del fichero.

        Raises:
            MissingParameterError: Si falta el medio o las rutas de salida
                derivadas de las marcas de tiempo.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        if not self.resolve_overwrite(output_list=self._expected_outputs()):
            sys.exit(0)

        self.logger.warning(msg=_("Remux cut may be imprecise."))

        cmd = CutCmd(params=self.params).create()

        self.display_cmd(cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=(_("Splitting media file")),
            progress_time=self.params.get_range_time(),
            output_list=self._expected_outputs(),
        )

        if self.params.timestamp_at is not None:
            self.logger.info(
                _("Container split successfully: %(count)d files."),
                count=len(self.params.timestamp_at) + 1,
            )
        else:
            self.logger.info(
                _("Container split successfully: %(output)s"),
                output=self.params.media_output,
            )

    def _expected_outputs(self) -> list[Path]:
        """Genera la lista de ficheros de salida en base a la cantidad de cortes.

        Raises:
            MissingParameterError: Si falta la ruta de salida procesada.
        """
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.timestamp_at is None:
            return [self.params.media_output]

        base_path = str(self.params.media_output)
        return [
            Path(base_path.replace("_%03d", f"_{i:03d}"))
            for i in range(len(self.params.timestamp_at) + 1)
        ]
