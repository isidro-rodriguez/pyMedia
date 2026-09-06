"""Mixin para operaciones con subtítulos."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pymedia.data.language_codes import LANGUAGES
from pymedia.errors import InvalidArgumentError, SubtitlesError
from pymedia.ffmpeg.probe import validate_subtitles_file_codec
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.models.media import Media
from pymedia.models.subtitle import Subtitle


class _HasMedia(Protocol):
    media: Media


class _HasMediaOutput(Protocol):
    media_output: Path


@dataclass(kw_only=True)
class SubtitlesInputMixin(_HasMedia, _HasMediaOutput):
    """Mixin para la recepción de ficheros de subtítulos.

    Attributes:
        subtitles: Objeto de metadatos para subtítulos.
    """

    subtitles: Subtitle | None = None

    def create_subtitle(
        self,
        subtitles_input: Path,
        language: str,
        logger: Logger,
        title: str | None = None,
        forced: bool = False,
        default: bool = False,
        hearing_impaired: bool = False,
        visual_impaired: bool = False,
    ) -> None:
        """Crea un modelo de metadatos de subtítulos.

        Modelo de metadatos que fuerza a indicar un código de idioma, según ISO 639-2, y
        genera el nombre nativo como título si no se ha aportado ninguno.

        Args:
            subtitles_input: Ruta del fichero de subtítulo a procesar.
            language: Lenguaje del fichero de subtítulos.
            logger: Interfaz principal de la aplicación para generar mensajes.
            title: Título descriptivo de la pista de subtítulos.
            forced: Si es una pista de subtítulos forzada a mostrar en el reproductor.
            default: Si es la pista de subtítulos por defecto del vídeo.
            hearing_impaired: Si están adaptados a personas con problemas auditivos.
            visual_impaired: Si están adaptados a personas con problemas visuales.

        Raises:
            InvalidArgumentError: si el idioma indicado no sigue el estándar ISO 639-2.
        """
        validate_subtitles_file_codec(subtitles_input=subtitles_input, logger=logger)
        language_code = self._parse_language(raw=language)
        self.subtitles = Subtitle(
            path=subtitles_input.absolute(),
            stream_index=self._process_stream_index(media=self.media),
            subtitles_index=self._process_subtitles_index(media=self.media),
            codec=self._process_codec(),
            language=language_code,
            title=self._process_subtitles_title(title=title, lang=language_code),
            forced=forced,
            default=default,
            hearing_impaired=hearing_impaired,
            visual_impaired=visual_impaired,
        )

    def _process_codec(self) -> str:
        match self.media_output.suffix:
            case ".m2ts" | ".mov" | ".mp4" | ".ts":
                return "mov_text"
            case ".mkv":
                return "srt"
            case ".webm":
                return "webvtt"

        raise SubtitlesError(msg=_("Subtitles codec not supported."))

    @staticmethod
    def _process_stream_index(media: Media) -> int:
        """Calcula el índice absoluto que ocupará el nuevo subtítulo en el output."""
        return (
            (1 if media.video is not None else 0)
            + len(media.audio or [])
            + len(media.subtitle or [])
        )

    @staticmethod
    def _process_subtitles_index(media: Media) -> int:
        """Calcula el próximo índice local de subtítulo (s:N) libre en el output."""
        return len(media.subtitle) if media.subtitle is not None else 0

    @staticmethod
    def _parse_language(raw: str) -> str:
        """Resuelve el idioma al código ISO 639-2 correspondiente."""
        normalized = raw.strip().casefold()
        for language in LANGUAGES.values():
            candidates = (
                language.code,
                language.english_name.casefold(),
                language.native_name.casefold(),
            )
            if normalized in candidates:
                return language.code
        raise InvalidArgumentError(
            msg=_(
                "Value doesn't match with ISO 639-2: "
                "Codes for the Representation of Names of Languages."
                "[https://www.loc.gov/standards/iso639-2/php/code_list.php]"
            )
        )

    @staticmethod
    def _process_subtitles_title(title: str | None, lang: str) -> str:
        """Utiliza el nombre del idioma como título si no lo ha indicado el usuario."""
        if title is not None:
            return title
        return LANGUAGES[lang].native_name
