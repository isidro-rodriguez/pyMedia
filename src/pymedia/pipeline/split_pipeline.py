"""Subcomando `split`: divide un contenedor en múltiples vídeos."""

from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.ffmpeg.split_cmd import SplitCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import SplitParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import OverwriteMode


class SplitPipeline(BasePipeline[SplitParameters]):
    """Comando de CLI para dividir un vídeo en múltiples ficheros de media."""

    def process_parameters(
        self,
        media_input: Path,
        overwrite: OverwriteMode,
        timestamp_at: str,
        media_output: Path | None = None,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params = SplitParameters(
            overwrite=overwrite,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        params.create_media_output(
            extension=self.config.default_containers.media,
            output=media_output,
            remux=True,
        )
        if params.media_output is None:
            raise MissingParameterError(name="params.media_output")
        output = params.media_output
        params.media_output = output.with_stem(f"{output.stem}_%03d")

        params.create_timestamp_at(times_str=timestamp_at)

        self.params = params

    def process_cmd(self) -> None:
        """Construye el comando ffmpeg y ejecuta la división de fichero multimedia."""
        if self.params.media is None:
            raise MissingParameterError(name="media")

        if not self.resolve_overwrite(output_list=self._resolve_output_list()):
            return

        cmd = SplitCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Splitting media file"),
            progress_time=self.params.media.duration,
        )

        self.logger.info(
            msg=_("Container split successfully: %(output)s"),
            output=self.params.media_output,
        )

    def _resolve_output_list(self) -> list[Path]:
        if self.params.timestamp_at is None:
            raise MissingParameterError(name="timestamp_at")

        base_path = str(self.params.media_output)
        path_list: list[Path] = []

        for i in range(len(self.params.timestamp_at)):
            base_path = base_path.replace("_%03d", f"_{i:3d}")
            path_list.append(Path(base_path))

        return path_list
