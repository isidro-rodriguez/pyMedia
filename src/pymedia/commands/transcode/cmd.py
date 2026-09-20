"""Comando ``transcode``: compositor de comandos ffmpeg."""

from pymedia.commands.transcode.parameters import TranscodeParameters
from pymedia.errors import MissingParameterError
from pymedia.models.config import Config
from pymedia.types import OverwriteMode


class TranscodeCmd:
    """Compone el comando de ffmpeg para transcodificar un contenedor."""

    def __init__(self, params: TranscodeParameters, config: Config) -> None:
        """Inicializa el generador con los parámetros validados de transcode.

        Args:
            params: Parámetros procesados del subcomando transcode.
            config: Parámetros que determinan el funcionamiento de la aplicación.
        """
        self.params = params
        self.config = config

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para transcodificar un contenedor.

        Returns:
            Lista de str con el comando de ffmpeg.

        Raises:
            MissingParameterError: Si no se pudo obtener los parámetros.
        """
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.media is None:
            raise MissingParameterError(name="media")

        subtitles_filter = ""
        if self.params.subtitles_input is not None:
            subtitles_filter = self.params.to_burn_subtitles_cmd()

        # Los subtítulos y los filtros de imagen viajan en un único grafo: el
        # filtro `-vf` no puede alimentarse de la salida de `-filter_complex`.
        filter_chain = ",".join(
            part for part in (subtitles_filter, self.params.to_filters_cmd()) if part
        )

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.extend(["-y"])

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
            ]
        )

        if filter_chain != "":
            cmd.extend(["-filter_complex", f"{filter_chain}[v]"])

        # Orden de salida estable: vídeo, audios y subtítulos.
        if self.params.media.video is not None:
            video_map = "[v]" if filter_chain != "" else "0:v:0"
            cmd.extend(["-map", video_map])

        if self.params.media.audio is not None:
            cmd.extend([*self.params.to_audio_transcode_cmd()])

        cmd.extend(
            [
                *self.params.to_subtitles_copy_cmd(
                    container=self.params.media_output.suffix
                ),
                *self.params.to_video_transcode_cmd(),
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd
