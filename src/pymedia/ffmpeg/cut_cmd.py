"""Compone el comando ffmpeg para cortar un vídeo."""

from pymedia.errors import MissingParameterError
from pymedia.models.parameters import CutParameters
from pymedia.types import OverwriteMode


class CutCmd:
    """Compone el comando ffmpeg para cortar un vídeo."""

    def __init__(self, params: CutParameters) -> None:
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

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.extend(["-y"])

        if self.params.timestamp_start is not None:
            cmd.extend(self.params.to_timestamp_start_cmd())

        if self.params.timestamp_end is not None:
            cmd.extend(self.params.to_timestamp_end_cmd())

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                "-map",
                "0",
                "-c",
                "copy",
            ]
        )

        if self.params.timestamp_at is not None:
            cmd.extend(self.params.to_timestamp_at_cmd())

        cmd.extend(
            [
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd
