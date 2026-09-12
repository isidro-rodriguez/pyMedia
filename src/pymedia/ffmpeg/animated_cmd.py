"""Composición de comandos ffmpeg para el subcomando `animated`."""

from pymedia.errors import MissingParameterError
from pymedia.models.parameters import AnimatedParameters
from pymedia.types import OverwriteMode


class AnimatedCmd:
    """Compone el comando de ffmpeg para generar imágenes animadas."""

    def __init__(self, params: AnimatedParameters) -> None:
        """Inicializa el generador con los parámetros validados de animated.

        Args:
            params: Parámetros procesados del subcomando animated.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para generar imágenes animadas.

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
        """Construye los filtros de ffmpeg para generar una imagen animada."""
        output = self.params.animated_output
        if output is None:
            raise MissingParameterError(name="animated_output")

        filters: list[str] = []

        filters_cmd = self.params.to_filters_cmd()
        if filters_cmd:
            filters.append(filters_cmd)

        filters.append(self.params.to_fps_cmd())

        if output.suffix == ".gif":
            filters.append(
                "split[a][b];[a]palettegen[p];[b][p]paletteuse=dither=floyd_steinberg"
            )

        return ",".join(filters)
