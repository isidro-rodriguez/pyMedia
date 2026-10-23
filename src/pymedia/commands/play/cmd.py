"""Comando ``play``: compositor de comandos ffplay."""

from datetime import timedelta

from pymedia.commands.play.parameters import PlayParameters
from pymedia.errors import MissingParameterError


class PlayCmd:
    """Compone el comando de ffplay para reproducir un vídeo."""

    def __init__(self, params: PlayParameters) -> None:
        """Inicializa el constructor de comando.

        Args:
            params: Parámetros parseados y validados para el comando ffplay.
        """
        self.params = params

    def create(self) -> list[str]:
        """Crea el comando de ffplay para reproducir el vídeo.

        Returns:
            Lista de cadenas de texto con el comando ffplay.

        Raises:
            MissingParameterError: Si no se pudo obtener el medio de entrada.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = ["ffplay"]

        start = self.params.timestamp_start
        if start is not None:
            cmd.extend(self.params.to_timestamp_start_cmd())

        # ffplay no admite `-to`: el final se expresa como duración desde el inicio.
        end = self.params.timestamp_end
        if end is not None:
            cmd.extend(["-t", str(end - (start or timedelta()))])

        overlay = (
            self.params.to_subtitles_overlay_cmd()
            if self.params.subtitles_input is not None
            else ""
        )
        filter_chain = ",".join(
            part for part in (overlay, self.params.to_filters_cmd()) if part
        )
        if filter_chain:
            cmd.extend(["-vf", filter_chain])

        cmd.extend(self.params.to_playback_cmd())
        cmd.append(str(self.params.media.path))

        return cmd
