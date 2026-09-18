"""Comando ``edit-subs``: compositor de comandos ffmpeg."""

from pymedia.commands.edit_subtitles.parameters import EditSubtitlesParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class EditSubtitlesCmd:
    """Compone el comando de ffmpeg para editar metadatos de subtítulos."""

    def __init__(self, params: EditSubtitlesParameters) -> None:
        """Inicializa el generador con los parámetros validados de edit-subs.

        Args:
            params: Parámetros procesados del comando edit-subs.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para editar subtítulos de un contenedor.

        Returns:
            Lista de cadenas con el comando ffmpeg listo para ejecutar.

        Raises:
            MissingParameterError: Si falta `media`, `media_output` o el
                modelo de subtítulos a editar.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.subtitles is None:
            raise MissingParameterError(name="subtitles")

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
                *self.params.to_subtitles_metadata_cmd(self.params.subtitles),
                *self.params.to_exclusive_default_cmd(),
                str(self.params.media_output),
            ]
        )

        return cmd
