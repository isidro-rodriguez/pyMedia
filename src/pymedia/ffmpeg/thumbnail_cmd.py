"""Composición de comandos ffmpeg para el subcomando thumbnail."""

from datetime import timedelta
from enum import Enum
from pathlib import Path

from pymedia.errors import MissingParameterError
from pymedia.models.pipeline.thumbnail_pipeline import ThumbnailParameters


class _ThumbnailMode(Enum):
    """Subtipos de thumbnails que soporta el generador."""

    TIMESTAMP = "timestamp"
    INTERVAL = "interval"
    SCENE = "scene"


class ThumbnailCmd:
    """Compone los comandos ffmpeg para generar thumbnails."""

    def __init__(self, params: ThumbnailParameters) -> None:
        self._params = params
        self._mode = self._resolve_mode()

    def create(self, timestamp: timedelta | None = None) -> list[str]:
        """Compone los comandos ffmpeg según el modo de thumbnail solicitado.

        Returns:
            Lista de comandos ffmpeg listos para consumo: uno por cada
            marca de tiempo en modo TIMESTAMP, o un único comando para
            los modos INTERVAL y SCENE (ffmpeg numera la salida).

        Raises:
            MissingParameterError: Si falta `output` o ningún parámetro
                de modo (`timestamp_at`, `scene`, `fps`) está presente.
        """
        if self._params.output is None:
            raise MissingParameterError(name="output")

        if self._mode is _ThumbnailMode.TIMESTAMP:
            if timestamp is None:
                raise MissingParameterError(name="timestamp_at")
            output = self._params.output.with_stem(
                f"{self._params.output.stem}_{str(timestamp)}"
            )
            return self._build_cmd(output=output, timestamp=timestamp)
        output = self._params.output.with_stem(f"{self._params.output.stem}_%03d")
        return self._build_cmd(output=output)

    def _resolve_mode(self) -> _ThumbnailMode:
        params = self._params
        if params.timestamp_at is not None:
            return _ThumbnailMode.TIMESTAMP
        if params.scene is not None:
            return _ThumbnailMode.SCENE
        if params.fps is not None:
            return _ThumbnailMode.INTERVAL
        raise MissingParameterError(name="timestamp_at, scene o fps")

    def _build_filters(self) -> str:
        """Construye los filtros de ffmpeg para generar thumbnails."""
        params = self._params
        filters: list[str] = []

        if self._mode is _ThumbnailMode.INTERVAL:
            filters.append(params.to_fps_cmd())

        if self._mode is _ThumbnailMode.SCENE:
            filters.append(params.to_scene_cmd())

        filters.append("thumbnail=30")
        filters.append(params.to_image_quality_cmd().format)

        if params.crop_area is not None:
            filters.append(params.to_crop_cmd())

        if params.scale_to is not None:
            scale_filter = params.to_scale_cmd()
            if scale_filter is not None:
                filters.append(scale_filter)

        if params.hflip or params.vflip:
            filters.append(params.to_flip_cmd())

        if params.rotate is not None:
            filters.append(params.to_rotate_cmd())

        return ",".join(filters)

    def _build_cmd(
        self,
        output: Path,
        timestamp: timedelta | None = None,
    ) -> list[str]:
        # Ensambla un único comando ffmpeg para el modo indicado
        params = self._params
        cmd: list[str] = ["ffmpeg", "-y"]

        if self._mode is _ThumbnailMode.TIMESTAMP:
            if timestamp is None:
                raise MissingParameterError(name="timestamp")
            cmd.extend(["-ss", str(timestamp)])
        else:
            if params.timestamp_start is not None:
                cmd.extend(params.to_timestamp_start_cmd())
            if params.timestamp_end is not None:
                cmd.extend(params.to_timestamp_end_cmd())

        cmd.extend(
            [
                *params.to_input_single_cmd(),
                "-vf",
                self._build_filters(),
            ]
        )

        if self._mode is _ThumbnailMode.TIMESTAMP:
            cmd.extend(["-frames:v", "1"])
        else:
            cmd.extend(["-fps_mode", "vfr"])

        cmd.extend([*params.to_image_quality_cmd().compression, str(output)])
        return cmd
