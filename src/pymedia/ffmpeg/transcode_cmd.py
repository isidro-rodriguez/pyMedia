"""Composición de comandos ffmpeg para el subcomando transcode."""

from pymedia.errors import MissingParameterError
from pymedia.models.config import Config
from pymedia.models.parameters import TranscodeParameters
from pymedia.types import OverwriteMode


class TranscodeCmd:
    """Compone el comando de ffmpeg para transcodificar un contenedor."""

    def __init__(self, params: TranscodeParameters, config: Config) -> None:
        """Inicializa el generador con los parámetros validados de transcode.

        Args:
            params: Parámetros procesados del subcomando transcode.
            config: Parámetros que determinan el funcionamiento de la aplicación.
        """
        self.params = params
        self.config = config

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para transcodificar un contenedor.

        Returns:
            Lista de str con el comando de ffmpeg.

        Raises:
            MissingParameterError: Si no se pudo obtener los parámetros.
        """
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.media is None:
            raise MissingParameterError(name="media")

        filters = self._build_filters()

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.extend(["-y"])

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
            ]
        )

        if filters is not None:
            cmd.extend(["-filter_complex", filters])

        if self.params.media.audio is not None:
            cmd.extend([*self.params.to_audio_transcode_cmd()])

        if self.params.media.video is not None:
            video_map = "[v]" if filters is not None else "0:v:0"
            cmd.extend(["-map", video_map])

        cmd.extend(
            [
                *self.params.to_video_transcode_cmd(),
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd

    def _build_filters(self) -> str | None:
        """Construye los filtros de ffmpeg."""
        output = self.params.media_output
        if output is None:
            raise MissingParameterError(name="media_output")

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

        if len(filters) > 0:
            return f"{','.join(filters)}[v]"
        return None
