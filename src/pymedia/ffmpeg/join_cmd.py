"""Compone el comando ffmpeg para unir vídeos."""

from pathlib import Path

from pymedia.errors import MissingParameterError
from pymedia.models.parameters import JoinParameters
from pymedia.types import OverwriteMode


class JoinCmd:
    """Compone el comando ffmpeg para unir múltiples vídeos."""

    def __init__(self, params: JoinParameters) -> None:
        """Inicializa el constructor de comando.

        Args:
            params: Parámetros parseados y validados para el comando ffmpeg.
        """
        self.params = params

    def create(self, list_txt: Path) -> list[str]:
        """Crea el comando de ffmpeg de unión de vídeos.

        Raises:
            MissingParameterError: Si `media` no se pudo obtener.

        Returns:
            Lista de cadenas de texto con el comando ffmpeg.
        """
        if self.params.media_list is None:
            raise MissingParameterError(name="media_list")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")
        else:
            cmd.append("-n")

        cmd.extend(
            [
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(list_txt),
                "-c",
                "copy",
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd
