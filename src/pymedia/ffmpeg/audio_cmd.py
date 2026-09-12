"""Composición de comandos ffmpeg para la familia de audio."""

from pathlib import Path

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.locales import _  # noqa
from pymedia.models.parameters import AudioParameters
from pymedia.types import OverwriteMode


class AudioCmd:
    """Compone los comandos ffmpeg para manipular audio."""

    def __init__(self, params: AudioParameters) -> None:
        """Inicializa el generador con los parámetros validados.

        Args:
            params: Parámetros procesados del subcomando ejecutado.
        """
        self.params = params

    def create_add_audio_cmd(self) -> list[str]:
        """Compone el comando de ffmpeg para insertar audio en contenedores."""
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
        if audio.path is None:
            raise MissingParameterError(name="audio.path")
        if audio.track_index is None:
            raise MissingParameterError(name="audio.track_index")
        if audio.title is None:
            raise MissingParameterError(name="audio.title")

        cmd = ["ffmpeg"]
        if self.params.overwrite == OverwriteMode.YES:
            cmd.extend(["-y"])

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
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd

    def create_delete_audio_cmd(self) -> list[str]:
        """Compone el comando de ffmpeg para eliminar audio en contenedores."""

        def _build_streams_list() -> list[str]:
            """Compone los mappings negativos de las pistas de audio a eliminar.

            `stream_tracks` guarda índices locales de audio (a:N), no los
            índices globales del contenedor, por lo que el selector ffmpeg usa
            el especificador de tipo `a`.
            """
            if self.params.stream_tracks is None:
                raise MissingParameterError(name="streams")
            str_list = []
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

    def create_edit_audio_cmd(self) -> list[str]:
        """Compone el comando de ffmpeg para editar audio en contenedores."""
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.media_output is None:
            raise MissingParameterError(name="media_output")
        if self.params.audio is None:
            raise MissingParameterError(name="audio")

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
                *self.params.to_audio_metadata_cmd(self.params.audio),
                *self.params.to_exclusive_default_cmd(),
                str(self.params.media_output),
            ]
        )

        return cmd

    def create_extract_audio_cmd(self) -> tuple[list[str], list[Path]]:
        """Compone el comando de ffmpeg para extraer audio en contenedores."""

        def _build_streams_list() -> list[str]:
            """Compone los mappings de las pistas de audio a extraer."""
            if self.params.stream_tracks is None:
                raise MissingParameterError(name="streams")
            if self.params.audio_output is None:
                raise MissingParameterError(name="audio_output")

            output = self.params.audio_output
            str_list = []
            for stream in self.params.stream_tracks:
                str_list.append("-map")
                str_list.append(f"0:a:{stream}")
                final_output = output.with_stem(f"{output.stem}_audio_track_{stream}")
                str_list.append(final_output)
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
