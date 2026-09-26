"""Comando ``extract-audio``: compositor de comandos ffmpeg."""

from pathlib import Path

from pymedia.commands.extract_audio.parameters import ExtractAudioParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class ExtractAudioCmd:
    """Compone el comando de ffmpeg para extraer pistas de audio."""

    def __init__(self, params: ExtractAudioParameters) -> None:
        """Inicializa el generador con los parámetros validados de extract-audio.

        Args:
            params: Parámetros procesados del comando extract-audio.
        """
        self.params = params

    def create(self) -> tuple[list[str], list[Path]]:
        """Compone el comando de ffmpeg para extraer audio de un contenedor.

        Returns:
            Tupla con la lista de cadenas del comando ffmpeg y las rutas de
            los ficheros de audio extraídos.

        Raises:
            MissingParameterError: Si falta `media`, el listado de pistas
                `stream_tracks` o la ruta `audio_output`.
        """

        def _build_streams_list() -> list[str]:
            """Compone los mappings de las pistas de audio a extraer."""
            if self.params.stream_tracks is None:
                raise MissingParameterError(name="streams")
            if self.params.audio_output is None:
                raise MissingParameterError(name="audio_output")

            output = self.params.audio_output
            str_list: list[str] = []
            for stream in self.params.stream_tracks:
                final_output = output.with_stem(f"{output.stem}_audio_track_{stream}")
                output_list.append(final_output)
                str_list.extend(
                    [
                        "-map",
                        f"0:a:{stream}",
                        "-c:a",
                        "copy",
                        str(final_output),
                    ]
                )
            return str_list

        if self.params.media is None:
            raise MissingParameterError(name="media")

        output_list: list[Path] = []
        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        cmd.extend(["-i", str(self.params.media.path)])

        if self.params.strip_metadata:
            cmd.extend(self.params.to_strip_metadata_cmd())

        cmd.extend([*_build_streams_list()])

        return cmd, output_list
