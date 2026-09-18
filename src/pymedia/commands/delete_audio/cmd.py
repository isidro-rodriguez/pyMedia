"""Comando ``delete-audio``: compositor de comandos ffmpeg."""

from pymedia.commands.delete_audio.parameters import DeleteAudioParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class DeleteAudioCmd:
    """Compone el comando de ffmpeg para eliminar pistas de audio."""

    def __init__(self, params: DeleteAudioParameters) -> None:
        """Inicializa el generador con los parámetros validados de delete-audio.

        Args:
            params: Parámetros procesados del comando delete-audio.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para eliminar audio de un contenedor.

        Returns:
            Lista de cadenas con el comando ffmpeg listo para ejecutar.

        Raises:
            MissingParameterError: Si falta `media`, `media_output` o el
                listado de pistas `stream_tracks` a eliminar.
        """

        def _build_streams_list() -> list[str]:
            """Compone los mappings negativos de las pistas de audio a eliminar.

            `stream_tracks` guarda índices locales de audio (a:N), no los
            índices globales del contenedor, por lo que el selector ffmpeg usa
            el especificador de tipo `a`.
            """
            if self.params.stream_tracks is None:
                raise MissingParameterError(name="streams")

            str_list: list[str] = []
            for stream in self.params.stream_tracks:
                str_list.append("-map")
                str_list.append(f"-0:a:{stream}")
            return str_list

        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                "-map",
                "0",
                *_build_streams_list(),
                "-c",
                "copy",
                str(self.params.media_output),
            ]
        )

        return cmd
