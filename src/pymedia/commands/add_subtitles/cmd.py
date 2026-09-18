"""Comando ``add-subs``: compositor de comandos ffmpeg."""

from pymedia.commands.add_subtitles.parameters import AddSubtitlesParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class AddSubtitlesCmd:
    """Compone el comando de ffmpeg para insertar una pista de subtítulos."""

    def __init__(self, params: AddSubtitlesParameters) -> None:
        """Inicializa el generador con los parámetros validados de add-subs.

        Args:
            params: Parámetros procesados del comando add-subs.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para insertar subtítulos en un contenedor.

        Returns:
            Lista de cadenas con el comando ffmpeg listo para ejecutar.

        Raises:
            MissingParameterError: Si falta `media`, `media_output` o algún
                campo requerido del modelo de subtítulos (`codec`, `language`,
                `path`, `track_index`, `title`).
        """
        subtitles = self.params.subtitles
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if subtitles is None:
            raise MissingParameterError(name="subtitles")
        if subtitles.codec is None:
            raise MissingParameterError(name="subtitles.codec")
        if subtitles.language is None:
            raise MissingParameterError(name="subtitles.language")
        if subtitles.path is None:
            raise MissingParameterError(name="subtitles.path")
        if subtitles.track_index is None:
            raise MissingParameterError(name="subtitles.track_index")
        if subtitles.title is None:
            raise MissingParameterError(name="subtitles.title")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                "-i",
                str(subtitles.path),
                "-map",
                "0",
                "-map",
                "1:0",
                "-c",
                "copy",
                f"-c:s:{subtitles.track_index}",
                subtitles.codec,
                *self.params.to_subtitles_metadata_cmd(subtitles=subtitles),
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd
