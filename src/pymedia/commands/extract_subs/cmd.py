"""Comando ``extract-subs``: compositor de comandos ffmpeg."""

from pathlib import Path

from pymedia.commands.extract_subs.parameters import ExtractSubtitlesParameters
from pymedia.errors import MissingParameterError
from pymedia.types import OverwriteMode


class ExtractSubtitlesCmd:
    """Compone el comando de ffmpeg para extraer pistas de subtítulos."""

    def __init__(self, params: ExtractSubtitlesParameters) -> None:
        """Inicializa el generador con los parámetros validados de extract-subs.

        Args:
            params: Parámetros procesados del comando extract-subs.
        """
        self.params = params

    def create(self) -> tuple[list[str], list[Path]]:
        """Compone el comando de ffmpeg para extraer subtítulos del contenedor.

        Returns:
            Tupla con la lista de cadenas del comando ffmpeg y las rutas de
            los ficheros de subtítulos extraídos.

        Raises:
            MissingParameterError: Si falta `media`, el listado de pistas
                `stream_tracks` o la ruta `subtitles_output`.
        """

        def _build_streams_list() -> list[str]:
            """Compone los mappings de las pistas de subtítulos a extraer.

            `stream_tracks` guarda índices locales de subtítulos (s:N), no los
            índices globales del contenedor, por lo que el selector ffmpeg usa
            el especificador de tipo `s`.
            """
            if self.params.stream_tracks is None:
                raise MissingParameterError(name="streams")
            if self.params.subtitles_output is None:
                raise MissingParameterError(name="subtitles_output")

            output = self.params.subtitles_output
            str_list: list[str] = []
            for stream in self.params.stream_tracks:
                str_list.append("-map")
                str_list.append(f"0:s:{stream}")
                final_output = output.with_stem(
                    f"{output.stem}_subtitles_track_{stream}"
                )
                str_list.append(str(final_output))
                output_list.append(final_output)
            return str_list

        if self.params.media is None:
            raise MissingParameterError(name="media")

        output_list: list[Path] = []
        cmd = ["ffmpeg"]

        if self.params.overwrite == OverwriteMode.YES:
            cmd.append("-y")

        cmd.extend(
            [
                "-i",
                str(self.params.media.path),
                *_build_streams_list(),
            ]
        )

        return cmd, output_list
