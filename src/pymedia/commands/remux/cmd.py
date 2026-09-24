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
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        container = self.params.media_output.suffix

        if self.params.sort_tracks:
            tracks = self.params.to_sort_tracks_cmd()
        else:
            tracks = ["-map", "0:v?", "-map", "0:a?", "-map", "0:s?"]

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        if self.params.rotate_metadata is not None:
            cmd.extend([*self.params.to_rotate_metadata_cmd()])

        if self.params.regenerate_pts:
            cmd.extend(self.params.to_regenerate_pts_cmd())

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                *tracks,
                "-c:v",
                "copy",
                "-c:a",
                "copy",
                "-c:s",
                "copy" if container != ".mp4" else "mov_text",
            ]
        )

        if container == ".mp4":
            cmd.extend(["-movflags", "+faststart"])

        cmd.append(str(self.params.media_output))

        return cmd
