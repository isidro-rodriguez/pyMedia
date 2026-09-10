"""Pipeline para la familia de subcomandos de capturas de imágenes."""

import math
import re
from datetime import timedelta
from pathlib import Path

import typer

from pymedia.errors import (
    CommandGenerationError,
    MissingParameterError,
)
from pymedia.ffmpeg.thumb_cmd import ThumbCmd
from pymedia.locales import _  # noqa
from pymedia.models.parameters import ThumbParameters
from pymedia.pipeline.base_pipeline import BasePipeline
from pymedia.types import OverwriteMode, RotateMode, ScaleMode, ThumbnailsMode


class ThumbPipeline(BasePipeline[ThumbParameters]):
    """Comando de CLI que genera miniaturas en modos timestamp, intervalo o escena."""

    def process_parameters(
        self,
        media_input: Path,
        thumbnails_mode: ThumbnailsMode,
        output: Path | None = None,
        overwrite: OverwriteMode = OverwriteMode.ASK,
        every: int | None = None,
        scene: float | None = None,
        timestamp_at: str | None = None,
        timestamp_start: str | None = None,
        timestamp_end: str | None = None,
        crop: str | None = None,
        rotate: RotateMode | None = None,
        scale_to: str | None = None,
        scale_mode: ScaleMode = ScaleMode.FIT,
        scale_upscale: bool = False,
        hflip: bool = False,
        vflip: bool = False,
    ) -> None:
        """Valida y parsea los argumentos en parámetros procesados.

        Attributes:
            media_input: Ruta del fichero de vídeo a procesar.
            output: Ruta absoluta del fichero de salida procesado.
            overwrite: Política ante conflicto de salida ya existente.
            every: Periodo, en segundos, entre capturas generadas.
            scene: Umbral de sensibilidad para detección de cambio de escena.
            timestamp_at: Lista de marcas de tiempo.
            timestamp_start: Marca de tiempo que indica el punto inicial.
            timestamp_end: Marca de tiempo que indica el punto final.
            crop: Área y coordenada de la zona a preservar de la imagen.
            rotate: Ángulo ortogonal con el que se va a rotar la imagen.
            scale_to: Dimensión objetivo en píxeles.
            scale_mode: Política de escalado del vídeo o imagen.
            scale_upscale: Permite el incremento de dimensiones.
            hflip: Invierte la imagen horizontalmente, intercambia izquierda y derecha.
            vflip: Invierte la imagen verticalmente, intercambiando arriba y abajo.
        """
        params = ThumbParameters(
            overwrite=overwrite,
            thumbnails_mode=thumbnails_mode,
        )

        params.create_media_input(
            media_input=media_input,
            logger=self.logger,
        )

        params.create_image_output(
            output=output,
            affix="_thumbnail",
            extension=self.config.default_containers.image,
        )

        params.create_timestamp_at(
            times_str=timestamp_at,
        )

        params.create_timestamp_start_end(
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
        )

        params.create_scene(
            scene=scene,
        )

        params.create_fps(
            every=every,
        )

        params.create_filters(
            logger=self.logger,
            crop=crop,
            scale_to=scale_to,
            scale_upscale=scale_upscale,
            scale_mode=scale_mode,
            rotate=rotate,
            hflip=hflip,
            vflip=vflip,
        )

        self.params = params

    def process_cmd(self) -> None:
        """Construye y ejecuta los comandos ffmpeg de las miniaturas."""
        if self.params.media is None:
            raise MissingParameterError(name="media")

        thumb_cmd = ThumbCmd(params=self.params)
        match self.params.thumbnails_mode:
            case ThumbnailsMode.FRAMES:
                if self.params.timestamp_at is None:
                    raise MissingParameterError(name="timestamp_at")
                for timestamp in self.params.timestamp_at:
                    cmd = thumb_cmd.create_frames_cmd(timestamp=timestamp)
                    self.resolve_overwrite([self._frames_output_path(timestamp)])
                    self._run_cmd(cmd=cmd)
            case ThumbnailsMode.INTERVAL:
                cmd = thumb_cmd.create_interval_cmd()
                output_list = self._resolve_interval_output_list(self.params)
                skip = False
                if self.params.overwrite == OverwriteMode.ASK:
                    skip = not self._resolve_overwrite_list(output_list)
                if not skip:
                    self._run_cmd(cmd=cmd)
            case ThumbnailsMode.SCENE:
                path = self.params.image_output
                if path is None:
                    raise MissingParameterError(name="image_output")
                cmd = thumb_cmd.create_scene_cmd()
                output_template = path.with_stem(f"{path.stem}_%03d")
                skip = False
                if self.params.overwrite == OverwriteMode.ASK:
                    skip = not self._resolve_scene_overwrite(output_template)
                if not skip:
                    self._run_cmd(cmd=cmd)

    def _frames_output_path(self, timestamp: timedelta) -> Path:
        """Devuelve la ruta de salida para un fotograma en timestamp dado."""
        if self.params.image_output is None:
            raise MissingParameterError(name="image_output")
        return self.params.image_output.with_stem(
            f"{self.params.image_output.stem}_{str(timestamp).replace(':', '-')}"
        )

    @staticmethod
    def _resolve_interval_output_list(params: ThumbParameters) -> list[Path]:
        """Genera la lista de outputs esperados para modo INTERVAL."""
        if params.image_output is None:
            raise MissingParameterError(name="image_output")
        if params.media is None or params.media.duration is None:
            raise MissingParameterError(name="media.duration")

        output: Path = params.image_output
        output_list: list[Path] = []
        duration_secs = params.media.duration.total_seconds()
        frames = duration_secs * params.fps
        counter = math.floor(frames)

        for i in range(counter):
            output_str = str(output)
            output_str = output_str.replace("_%03d", f"_{i:3d}")
            output_list.append(Path(output_str))
        return output_list

    def _resolve_overwrite_list(self, output_list: list[Path]) -> bool:
        """Pregunta al usuario por cada archivo existente en la lista."""
        for output in output_list:
            if output.exists():
                self.logger.warning(_(f"Output file already exists: {output.name}"))
                if not typer.confirm(_("Overwrite?")):
                    self.logger.warning(
                        _("Process skipped since output file already exists.")
                    )
                    return False
        return True

    def _resolve_scene_overwrite(self, output_template: Path) -> bool:
        """Detecta si existen archivos con patrón 'filename_XXX.ext'."""
        # Construir regex a partir del template
        stem = output_template.stem  # ej: thumbnails_%03d
        suffix = output_template.suffix  # ej: .jpg
        # Extraer la parte fija antes del %03d
        match = re.match(r"^(.+)_%03d$", stem)
        if not match:
            # Si no hay patrón reconocible, se aborta para seguridad
            self.logger.warning(_("Cannot resolve scene output pattern from template."))
            return False
        base_stem = match.group(1)  # ej: thumbnails

        # Directorio donde se escribirán los archivos
        directory = output_template.parent
        pattern = re.compile(rf"^{re.escape(base_stem)}_(\d{3}){re.escape(suffix)}$")

        # Buscar archivos existentes
        existing_files = []
        if directory.exists():
            for item in directory.iterdir():
                if item.is_file() and pattern.match(item.name):
                    existing_files.append(item)

        if existing_files:
            self.logger.warning(
                _("Found existing scene thumbnail files: %(files)s")
                % {"files": ", ".join(f.name for f in existing_files)}
            )
            if not typer.confirm(_("Overwrite?")):
                self.logger.warning(
                    _("Process skipped since output files already exist.")
                )
                return False
        return True

    def _run_cmd(self, cmd: list[str]) -> None:
        """Ejecuta un comando ffmpeg de miniaturas y registra el resultado."""
        if cmd is None:
            raise CommandGenerationError(name=self.command_name)
        if self.params.media is None:
            raise MissingParameterError(name="media")

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            progress_time=self.params.get_range_time(),
            description=_("Generating thumbnail"),
        )

        self.logger.info(
            msg=_("Thumbnail(s) generated successfully: %(output)s"),
            output=self.params.image_output,
        )
