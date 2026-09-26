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
                campo requerido del modelo de audio (`codec`, `path`,
                `track_index`).
        """
        audio = self.params.audio
        media = self.params.media
        if media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if audio is None:
            raise MissingParameterError(name="audio")

        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        if self.params.strip_metadata:
            cmd.extend(self.params.to_strip_metadata_cmd())

        cmd.extend(
            [
                "-i",
                str(media.path),
                "-i",
                str(audio[0].path),
                "-map",
                "0",
                "-map",
                "1:a",
                "-c",
                "copy",
            ]
        )

        # Copiar metadatos de la pista de audio origen (idioma, título)
        # estableciéndolos explícitamente en el output, ya que -c copy con -map
        # no siempre preserva todos los tags de stream.
        if audio and media.audio is not None:
            # El índice de la primera pista importada en el output es:
            # 1 (video) + len(media.audio) (audio streams from input 0)
            output_audio_index = (1 if media.video is not None else 0) + len(
                media.audio
            )
            for track in audio:
                if track.track_index is not None:
                    meta = track.metadata
                    if meta.language:
                        cmd.extend(
                            [
                                f"-metadata:s:a:{output_audio_index}",
                                f"language={meta.language}",
                            ]
                        )
                    if meta.title:
                        cmd.extend(
                            [
                                f"-metadata:s:a:{output_audio_index}",
                                f"title={meta.title}",
                            ]
                        )
                    output_audio_index += 1

        # Resetear disposiciones de las pistas importadas solo si el contenedor
        # ya tenía audio previo. En ese caso, ffmpeg hereda las disposiciones
        # del archivo origen, y queremos empezar en 0 para que el usuario decida
        # con edit-audio. Si no había audio previo, las disposiciones del
        # archivo origen se conservan (comportamiento heredado).
        if media.audio:
            cmd.extend([*self._reset_imported_defaults_args()])

        cmd.extend(
            [
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd

    def _reset_imported_defaults_args(self) -> list[str]:
        """Retira todas las disposiciones de las pistas de audio importadas.

        Se usa cuando el contenedor destino ya tenía audio, para evitar que
        las disposiciones del archivo origen se propaguen sin control.
        """
        if self.params.audio is None:
            raise MissingParameterError(name="audio")

        args: list[str] = []
        for track in self.params.audio:
            if track.track_index is None:
                raise MissingParameterError(name="audio.track_index")
            args.extend([f"-disposition:a:{track.track_index}", "0"])
        return args
