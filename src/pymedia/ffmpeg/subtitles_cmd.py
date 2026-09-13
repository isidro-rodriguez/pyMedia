"""Composición de comandos ffmpeg para la familia de subtítulos."""

from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.locales import _  # noqa
from pymedia.models.parameters import SubtitlesParameters
from pymedia.types import OverwriteMode


class SubtitlesCmd:
    """Compone los comandos ffmpeg para manipular subtítulos."""

    def __init__(self, params: SubtitlesParameters) -> None:
        """Inicializa el generador con los parámetros validados.

        Args:
            params: Parámetros procesados del subcomando ejecutado.
        """
        self.params = params

    def create_add_subtitles_cmd(self) -> list[str]:
        """Compone el comando de ffmpeg para insertar subtítulos en contenedores.

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
            cmd.extend(["-y"])

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

    def create_delete_subtitles_cmd(self) -> list[str]:
        """Compone el comando de ffmpeg para eliminar subtítulos en contenedores.

        Returns:
            Lista de cadenas con el comando ffmpeg listo para ejecutar.

        Raises:
            MissingParameterError: Si falta `media`, `media_output` o el
                listado de pistas `streams` a eliminar.
        """

        def _build_streams_list() -> list[str]:
            """Compone los mappings negativos de las pistas de subtítulos a eliminar.

            `stream_tracks` guarda índices locales de subtítulos (s:N), no los
            índices globales del contenedor, por lo que el selector ffmpeg usa
            el especificador de tipo `s`.
            """
            if self.params.stream_tracks is None:
                raise MissingParameterError(name="streams")
            str_list = []
            for stream in self.params.stream_tracks:
                str_list.append("-map")
                str_list.append(f"-0:s:{stream}")
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

    def create_edit_subtitles_cmd(self) -> list[str]:
        """Compone el comando de ffmpeg para editar subtítulos en contenedores.

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

    def create_extract_subtitles_cmd(self) -> tuple[list[str], list[Path]]:
        """Compone el comando de ffmpeg para extraer subtítulos en contenedores.

        Returns:
            Tupla con la lista de cadenas del comando ffmpeg y las rutas de
            los ficheros de subtítulos extraídos.

        Raises:
            MissingParameterError: Si falta `media`, el listado de pistas
                `streams` o la ruta `subtitles_output`.
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
