"""Comando ``animated``: compositor de comandos ffmpeg."""

from pymedia.commands.animated.parameters import AnimatedParameters
from pymedia.errors import InvalidParameterError, MissingParameterError
from pymedia.locales import translate as _
from pymedia.types import OverwriteMode, ScaleFlag


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
                *self._build_args_per_animated_container(),
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.animated_output),
            ]
        )

        return cmd

    def _build_filters(self) -> str:
        """Construye los filtros de ffmpeg para generar una imagen animada."""
        if self.params.animated_output is None:
            raise MissingParameterError(name="animated_output")

        filters: list[str] = []

        filters_cmd = self.params.to_filters_cmd(scale_flag=ScaleFlag.LANCZOS)
        if filters_cmd:
            filters.append(filters_cmd)

        filters.append(self.params.to_fps_cmd())

        match self.params.animated_output.suffix:
            case ".apng":
                filters.append(
                    "split[a][b];[a]palettegen=max_colors=256:stats_mode=diff[p];"
                    "[b][p]paletteuse=dither=sierra2_4a"
                )
            case ".gif":
                filters.append(
                    "split[a][b];[a]palettegen[p];"
                    "[b][p]paletteuse=dither=floyd_steinberg"
                )
            case _:
                pass

        return ",".join(filters)

    def _build_args_per_animated_container(self) -> list[str]:
        """Establece opciones dependiendo del contenedor de salida."""
        if self.params.animated_output is None:
            raise MissingParameterError(name="animated_output")

        args: list[str] = []

        match self.params.animated_output.suffix:
            case ".apng":
                return [
                    "-c:v",
                    "apng",
                    "-compression_level",
                    "9",
                    "-plays",
                    "0",
                ]
            case ".gif":
                return [
                    "-loop",
                    "0",
                ]
            case ".webp":
                return [
                    "-c:v",
                    "libwebp_anim",
                    "-lossless",
                    "0",
                    "-quality",
                    "80",
                    "-compression_level",
                    "6",
                    "-loop",
                    "0",
                ]
            case _:
                raise InvalidParameterError(
                    msg=_("Animated image output not supported")
                )

        return args
