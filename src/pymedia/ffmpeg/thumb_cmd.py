"""Composición de comandos ffmpeg para el subcomando thumbnail."""

from datetime import timedelta
from enum import Enum
from pathlib import Path

from pymedia.errors import MissingParameterError
from pymedia.models.parameters import ThumbParameters
from pymedia.types import OverwriteMode


class _ScreenshootMode(Enum):
    """Subtipos de thumbnails que soporta el generador."""

    INTERVAL = "interval"
    FRAMES = "frames"
    SCENE = "scene"


class ThumbCmd:
    """Compone los comandos ffmpeg para generar thumbnails."""

    def __init__(self, params: ThumbParameters) -> None:
        """Inicializa el generador y resuelve el modo de thumbnail.

        Args:
            params: Parámetros procesados del subcomando thumbnail.
        """
        self.params = params
        self._mode = self._resolve_mode()

    def create(self, timestamp: timedelta | None = None) -> list[str]:
        """Compone los comandos ffmpeg según el modo de thumbnail solicitado.

        Args:
            timestamp: Marca de tiempo del fotograma a capturar (modo TIMESTAMP).

        Returns:
            Lista de comandos ffmpeg listos para consumo: uno por cada
            marca de tiempo en modo TIMESTAMP, o un único comando para
            los modos INTERVAL y SCENE (ffmpeg numera la salida).

        Raises:
            MissingParameterError: Si falta `output` o ningún parámetro
                de modo (`timestamp_at`, `scene`, `fps`) está presente.
        """
        if self.params.image_output is None:
            raise MissingParameterError(name="image_output")

        if self._mode is _ScreenshootMode.FRAMES:
            if timestamp is None:
                raise MissingParameterError(name="timestamp_at")
            output = self.params.image_output.with_stem(
                f"{self.params.image_output.stem}_{str(timestamp).replace(':', '-')}"
            )
            return self._build_cmd(output=output, timestamp=timestamp)
        output = self.params.image_output.with_stem(
            f"{self.params.image_output.stem}_%03d"
        )
        return self._build_cmd(output=output)

    def _resolve_mode(self) -> _ScreenshootMode:
        """Establece el modo de obtención de imágenes para mayor claridad de módulo."""
        params = self.params
        if params.timestamp_at is not None:
            return _ScreenshootMode.FRAMES
        if params.scene is not None:
            return _ScreenshootMode.SCENE
        if params.fps is not None:
            return _ScreenshootMode.INTERVAL
        raise MissingParameterError(name="timestamp_at, scene o fps")

    def _build_filters(self) -> str:
        """Construye los filtros de ffmpeg para generar thumbnails."""
        params = self.params
        filters: list[str] = []

        match self._mode:
            case _ScreenshootMode.FRAMES:
                filters.append("thumbnail=30")
            case _ScreenshootMode.INTERVAL:
                filters.append("thumbnail=30")
                filters.append(params.to_fps_cmd())
            case _ScreenshootMode.SCENE:
                filters.append(params.to_scene_cmd())

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
        """Ensambla un único comando ffmpeg para el modo indicado."""
        params = self.params
        if params.media is None:
            raise MissingParameterError(name="media")

        cmd: list[str] = ["ffmpeg"]

        if self.params.overwrite is OverwriteMode.YES:
            cmd.append("-y")
        else:
            cmd.append("-n")

        if self._mode is _ScreenshootMode.FRAMES:
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
                "-i",
                str(params.media.path),
                "-vf",
                self._build_filters(),
            ]
        )

        if self._mode is _ScreenshootMode.FRAMES:
            cmd.extend(["-frames:v", "1"])
        else:
            cmd.extend(["-fps_mode", "vfr"])

        cmd.extend(
            [
                *params.to_image_quality_cmd().compression,
                "-progress",
                "pipe:1",
                "-nostats",
                str(output),
            ]
        )
        return cmd
