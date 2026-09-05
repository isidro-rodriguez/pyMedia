"""Composición de comandos ffmpeg para el subcomando gif."""

from pymedia.errors import MissingParameterError
from pymedia.models.parameters import GifParameters
from pymedia.types import OverwriteMode


class GifCmd:
    """Compone el comando de ffmpeg para generar animaciones en Gifs."""

    def __init__(self, params: GifParameters) -> None:
        """Inicializa el generador con los parámetros validados del GIF.

        Args:
            params: Parámetros procesados del subcomando gif.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para generar animaciones en Gifs.

        Returns:
            Lista de str con el comando de ffmpeg.

        Raises:
            MissingParameterError: Si no se pudo obtener los parámetros.
        """
        if self.params.animated_output is None:
            raise MissingParameterError(name="animated_output")
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.extend(["-y"])

        if self.params.timestamp_start:
            cmd.extend(self.params.to_timestamp_start_cmd())

        if self.params.timestamp_end:
            cmd.extend(self.params.to_timestamp_end_cmd())

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                "-filter_complex",
                self._build_filters(),
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.animated_output),
            ]
        )

        return cmd

    def _build_filters(self) -> str:
        """Construye los filtros de ffmpeg para generar un Gif."""
        output = self.params.animated_output
        if output is None:
            raise MissingParameterError(name="animated_output")

        filters: list[str] = []

        if self.params.crop_area is not None:
            filters.append(self.params.to_crop_cmd())

        if self.params.scale_to is not None:
            scale_filter = self.params.to_scale_cmd()
            if scale_filter is not None:
                filters.append(scale_filter)

        if self.params.hflip or self.params.vflip:
            filters.append(self.params.to_flip_cmd())

        if self.params.rotate is not None:
            filters.append(self.params.to_rotate_cmd())

        filters.append(self.params.to_fps_cmd())

        if output.suffix == ".gif":
            filters.append(
                "split[a][b];[a]palettegen[p];[b][p]paletteuse=dither=floyd_steinberg"
            )

        return ",".join(filters)
