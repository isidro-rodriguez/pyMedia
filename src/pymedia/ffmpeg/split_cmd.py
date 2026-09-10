"""Compone el comando ffmpeg para dividir un vídeo."""

from pymedia.errors import MissingParameterError
from pymedia.models.parameters import SplitParameters
from pymedia.types import OverwriteMode


class SplitCmd:
    """Compone el comando ffmpeg para dividir un vídeo."""

    def __init__(self, params: SplitParameters) -> None:
        """Inicializa el constructor de comando.

        Args:
            params: Parámetros parseados y validados para el comando ffmpeg.
        """
        self.params = params

    def create(self) -> list[str]:
        """Crea el comando de ffmpeg.

        Raises:
            MissingParameterError: Si `media` o `timestamp_at` no se pueden obtener.

        Returns:
            Lista de cadenas de texto con el comando ffmpeg.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.timestamp_at is None:
            raise MissingParameterError(name="timestamp_at")

        times_str = ",".join(str(t) for t in self.params.timestamp_at)

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.extend(["-y"])

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                "-map",
                "0",
                "-c",
                "copy",
                "-f",
                "segment",
                "-segment_times",
                times_str,
                "-reset_timestamps",
                "1",
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd
