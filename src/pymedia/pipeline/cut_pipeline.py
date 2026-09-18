"""Subcomando `cut`: divide un contenedor en múltiples vídeos."""

import sys
from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.ffmpeg.cut_cmd import CutCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import CutParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import OverwriteMode


class CutPipeline(BasePipeline[CutParameters]):
    """Comando de CLI para el corte de un vídeo."""

    def process_parameters(
        self,
        media_input: Path,
        overwrite: OverwriteMode,
        timestamp_at: str | None = None,
        timestamp_start: str | None = None,
        timestamp_end: str | None = None,
        media_output: Path | None = None,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados.

        Args:
            media_input: Ruta del fichero de vídeo a procesar.
            overwrite: Política ante conflicto de salida ya existente.
            timestamp_at: Lista de marcas de tiempo para dividir el vídeo.
            timestamp_start: Corte inicial del vídeo de salida.
            timestamp_end: Corte final del vídeo de salida.
            media_output: Ruta absoluta del fichero de salida procesado.

        Raises:
            MissingParameterError: Si la salida procesada no se pudo obtener.
        """
        params = CutParameters(
            overwrite=overwrite,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        params.create_media_output(
            extension=self.config.default_containers.media,
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

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la división de fichero multimedia.

        Raises:
            MissingParameterError: Si falta el medio o las rutas de salida
                derivadas de las marcas de tiempo.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        if not self.resolve_overwrite(output_list=self._expected_outputs()):
            sys.exit(0)

        cmd = CutCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Splitting media file"),
            progress_time=self.params.get_range_time(),
            output_list=self._expected_outputs(),
        )

        if self.params.timestamp_at is not None:
            self.logger.info(
                _("Container split successfully: %(count)d files."),
                count=len(self.params.timestamp_at),
            )
        else:
            self.logger.info(
                _("Container split successfully: %(output)s"),
                output=self.params.media_output,
            )

    def _expected_outputs(self) -> list[Path]:
        """Genera la lista de ficheros de salida en base a la cantidad de cortes."""
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.timestamp_at is None:
            return [self.params.media_output]

        base_path = str(self.params.media_output)
        return [
            Path(base_path.replace("_%03d", f"_{i:03d}"))
            for i in range(len(self.params.timestamp_at) + 1)
        ]
