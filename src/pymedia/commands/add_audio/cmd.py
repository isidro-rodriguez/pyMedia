"""Comando ``add-audio``: compositor de comandos ffmpeg."""

from pymedia.commands.add_audio.parameters import AddAudioParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class AddAudioCmd:
    """Compone el comando de ffmpeg para insertar una pista de audio."""

    def __init__(self, params: AddAudioParameters) -> None:
        """Inicializa el generador con los parámetros validados de add-audio.

        Args:
            params: Parámetros procesados del comando add-audio.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para insertar audio en un contenedor.

        Returns:
            Lista de cadenas con el comando ffmpeg listo para ejecutar.

        Raises:
            MissingParameterError: Si falta `media`, `media_output` o algún
                campo requerido del modelo de audio (`codec`, `language`,
                `path`, `track_index`, `title`).
        """
        audio = self.params.audio
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if audio is None:
            raise MissingParameterError(name="audio")
        if audio.codec is None:
            raise MissingParameterError(name="audio.codec")
        if audio.language is None:
            raise MissingParameterError(name="audio.language")
        if audio.track_index is None:
            raise MissingParameterError(name="audio.track_index")
        if audio.title is None:
            raise MissingParameterError(name="audio.title")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        if self.params.strip_metadata:
            cmd.extend(self.params.to_strip_metadata_cmd())

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                "-i",
                str(audio.path),
                "-map",
                "0",
                "-map",
                "1:0",
                "-c",
                "copy",
                f"-c:a:{audio.track_index}",
                audio.codec,
                *self.params.to_audio_metadata_cmd(audio=audio),
                *self.params.to_exclusive_default_cmd(),
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd
