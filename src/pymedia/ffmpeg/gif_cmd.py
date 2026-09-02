from pymedia.data.types import OverwriteMode
from pymedia.errors import MissingParameterError
from pymedia.models.pipeline.gif_pipeline import GifParameters


class GifCmd:
    """Compone el comando de ffmpeg para generar animaciones en Gifs."""

    def __init__(self, params: GifParameters) -> None:
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para generar animaciones en Gifs

        Returns:
            Lista de str con el comando de ffmpeg.

        Raises:
            MissingParameterError: Si no se pudo obtener los parámetros.
        """
        if self.params.output is None:
            raise MissingParameterError(name="output")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.extend(["-y"])

        if self.params.timestamp_start:
            cmd.extend(self.params.to_timestamp_start_cmd())

        if self.params.timestamp_end:
            cmd.extend(self.params.to_timestamp_end_cmd())

        cmd.extend(
            [
                *self.params.to_input_single_cmd(),
                "-filter_complex",
                self._build_filters(),
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.output),
            ]
        )

        return cmd

    def _build_filters(self) -> str:
        """Construye los filtros de ffmpeg para generar un Gif."""
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

        filters.append(
            "split[a][b];[a]palettegen[p];[b][p]paletteuse=dither=floyd_steinberg"
        )

        return ",".join(filters)
