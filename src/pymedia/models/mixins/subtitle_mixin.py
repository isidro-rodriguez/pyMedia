"""Mixin para operaciones con subtítulos."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pymedia.data.language_codes import LANGUAGES
from pymedia.errors import InvalidArgumentError
from pymedia.ffmpeg.probe import validate_subtitle_codec
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.models.media import Media
from pymedia.models.subtitle import Subtitle


class _HasMedia(Protocol):
    media: Media


@dataclass(kw_only=True)
class SubtitleInputMixin(_HasMedia):
    """Mixin para la recepción de ficheros de subtítulos.

    Attributes:
        subtitle:
    """

    subtitle: Subtitle

    def create_subtitle(
        self,
        subtitle_input: Path,
        lang: str,
        media: Media,
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
            subtitle_input: Ruta del fichero de subtítulo a procesar.
            lang: Lenguaje del fichero de subtítulos.
            media: Metadatos del vídeo de entrada ya resuelto y validado.
            logger: Interfaz principal de la aplicación para generar mensajes.
            title: Título descriptivo de la pista de subtítulos.
            forced: Si es una pista de subtítulos forzada a mostrar en el reproductor.
            default: Si es la pista de subtítulos por defecto del vídeo.
            hearing_impaired: Si están adaptados a personas con problemas auditivos.
            visual_impaired: Si están adaptados a personas con problemas visuales.

        Raises:
            InvalidArgumentError: si el idioma indicado no sigue el estándar ISO 639-2.
        """
        language_code = self._parse_language(raw=lang)
        self.subtitle = Subtitle(
            path=subtitle_input.absolute(),
            index=self._process_subtitle_index(media=media),
            codec=validate_subtitle_codec(path=subtitle_input, logger=logger),
            language=language_code,
            title=self._process_subtitle_title(title=title, lang=language_code),
            forced=forced,
            default=default,
            hearing_impaired=hearing_impaired,
            visual_impaired=visual_impaired,
        )

    @staticmethod
    def _process_subtitle_index(media: Media) -> int:
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
    def _process_subtitle_title(title: str | None, lang: str) -> str:
        """Utiliza el nombre del idioma como título si no lo ha indicado el usuario."""
        if title is not None:
            return title
        return LANGUAGES[lang].native_name
