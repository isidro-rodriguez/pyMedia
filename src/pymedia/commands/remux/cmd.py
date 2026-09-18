"""Comando ``remux``: compositor de comandos ffmpeg."""

from pymedia.commands.remux.parameters import RemuxParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class RemuxCmd:
    """Compone el comando de ffmpeg para remux."""

    def __init__(self, params: RemuxParameters) -> None:
        """Inicializa el constructor de comando.

        Args:
            params: Parámetros parseados y validados para el comando ffmpeg.
        """
        self.params = params

    def create(self) -> list[str]:
        """Crea el comando de ffmpeg para remux.

        Raises:
            MissingParameterError: Si no se pudo obtener algún parámetro.

        Returns:
            Lista de cadenas de texto con el comando ffmpeg.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        if self.params.regenerate_pts:
            cmd.extend(self.params.to_regenerate_pts_cmd())

        cmd.extend(["-i", str(self.params.media.path)])

        if self.params.sort_tracks:
            cmd.extend(self.params.to_sort_tracks_cmd())
        else:
            cmd.extend(["-map", "0"])

        cmd.extend(["-c", "copy"])

        if self.params.fast_start:
            cmd.extend(self.params.to_fast_start_cmd())

        cmd.append(str(self.params.media_output))

        return cmd
