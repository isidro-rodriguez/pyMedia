"""Comando ``edit-audio``: compositor de comandos ffmpeg."""

from pymedia.commands.edit_audio.parameters import EditAudioParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class EditAudioCmd:
    """Compone el comando de ffmpeg para editar metadatos de una pista de audio."""

    def __init__(self, params: EditAudioParameters) -> None:
        """Inicializa el generador con los parámetros validados de edit-audio.

        Args:
            params: Parámetros procesados del comando edit-audio.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para editar audio de un contenedor.

        Returns:
            Lista de cadenas con el comando ffmpeg listo para ejecutar.

        Raises:
            MissingParameterError: Si falta `media`, `media_output` o el
                modelo de audio a editar.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.audio is None:
            raise MissingParameterError(name="audio")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                "-map",
                "0",
                "-c",
                "copy",
                *self.params.to_audio_metadata_cmd(self.params.audio),
                *self.params.to_exclusive_default_cmd(),
                str(self.params.media_output),
            ]
        )

        return cmd
