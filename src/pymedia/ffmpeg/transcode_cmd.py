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

        filters = self.params.to_filters_cmd()

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
            cmd.extend(["-filter_complex", f"{filters}[v]"])

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
