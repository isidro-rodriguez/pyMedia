"""Composición de comando ffmpeg para la adición de subtítulos."""

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.locales import _  # noqa
from pymedia.models.parameters import SubtitlesAddParameters
from pymedia.types import OverwriteMode


class SubtitlesAddCmd:
    """Compone el comando ffmpeg para insertar subtítulos en contenedores multimedia."""

    def __init__(self, params: SubtitlesAddParameters) -> None:
        """Inicializa el generador con los parámetros validados.

        Args:
            params: Parámetros procesados del subcomando `subtitles add`.
        """
        self.params = params

    def create(self) -> list[str]:
        """Compone el comando de ffmpeg para insertar subtítulos en contenedores.

        Returns:
            Lista de str con el comando de ffmpeg.

        Raises:
            MissingParameterError: Si no se pudo obtener algún parámetro.
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
        if subtitles.stream_index is None:
            raise MissingParameterError(name="subtitles.stream_index")
        if subtitles.subtitles_index is None:
            raise MissingParameterError(name="subtitles.subtitles_index")
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
                f"-c:s:{subtitles.subtitles_index}",
                subtitles.codec,
                f"-metadata:s:{subtitles.stream_index}",
                f"language={subtitles.language}",
                f"-metadata:s:{subtitles.stream_index}",
                f"title={subtitles.title}",
                *self._build_subtitles_dispositions(),
                "-progress",
                "pipe:1",
                "-nostats",
                str(self.params.media_output),
            ]
        )

        return cmd

    def _build_subtitles_dispositions(self) -> list[str]:
        """Construye los flags de disposiciones para la pista de subtítulos."""
        subtitles = self.params.subtitles
        if subtitles is None:
            raise MissingParameterError(name="subtitles")
        if subtitles.subtitles_index is None:
            raise MissingParameterError(name="subtitles.subtitles_index")

        dispositions: list[str] = []

        if subtitles.forced:
            dispositions.append("forced")
        if subtitles.default:
            dispositions.append("default")
        if subtitles.hearing_impaired:
            dispositions.append("hearing_impaired")
        if subtitles.visual_impaired:
            dispositions.append("visual_impaired")

        return [
            f"-disposition:s:{subtitles.subtitles_index}",
            "+".join(dispositions) if len(dispositions) > 0 else "0",
        ]
