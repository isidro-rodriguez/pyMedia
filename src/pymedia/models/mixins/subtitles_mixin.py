"""Mixin para operaciones con subtítulos."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pymedia.data.language_codes import LANGUAGES
from pymedia.errors import (
    InvalidArgumentError,
    MissingArgumentError,
    MissingParameterError,
    SubtitlesError,
)
from pymedia.ffmpeg.probe import validate_subtitles_file_codec
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.models.media import Media
from pymedia.models.subtitles import Subtitles


class _SubtitlesContext(Protocol):
    media: Media
    media_output: Path
    stream_tracks: list[int]


@dataclass(kw_only=True)
class SubtitlesInputMixin(_SubtitlesContext):
    """Mixin para la recepción de ficheros de subtítulos.

    Attributes:
        subtitles: Objeto de metadatos para subtítulos.
    """

    subtitles: Subtitles | None = None

    def create_add_subtitles(
        self,
        subtitles_input: Path,
        logger: Logger,
        language: str | None = None,
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
            InvalidArgumentError: Si el idioma indicado no sigue el estándar ISO 639-2.
            MissingArgumentError: Si no se recibió el argumento `language`.
            SubtitlesError: Si el contenedor de salida no tiene un códec de
                subtítulos soportado.
        """
        if language is None:
            raise MissingArgumentError(name=_("subtitles language"))

        validate_subtitles_file_codec(subtitles_input=subtitles_input, logger=logger)
        language_code = self._parse_language(raw=language)
        self.subtitles = Subtitles(
            path=subtitles_input.absolute(),
            global_index=self._process_stream_index(media=self.media),
            track_index=self._process_subtitles_index(media=self.media),
            codec=self._process_codec(),
            language=language_code,
            title=self._process_subtitles_title(title=title, lang=language_code),
            forced=forced,
            default=default,
            hearing_impaired=hearing_impaired,
            visual_impaired=visual_impaired,
        )

    def create_edit_subtitles(
        self,
        language: str | None = None,
        title: str | None = None,
        forced: bool | None = None,
        default: bool | None = None,
        hearing_impaired: bool | None = None,
        visual_impaired: bool | None = None,
    ) -> None:
        """Crea un modelo de metadatos de subtítulos para editar los de un contenedor.

        Args:
            language: Lenguaje del fichero de subtítulos.
            title: Título descriptivo de la pista de subtítulos.
            forced: Si es una pista de subtítulos forzada a mostrar en el reproductor.
            default: Si es la pista de subtítulos por defecto del vídeo.
            hearing_impaired: Si están adaptados a personas con problemas auditivos.
            visual_impaired: Si están adaptados a personas con problemas visuales.

        Raises:
            InvalidArgumentError: Si el idioma indicado no sigue el estándar ISO 639-2.
            MissingParameterError: Si no se recibió el listado de pistas o los
                metadatos del medio.
            SubtitlesError: Si la pista indicada no existe en el contenedor.
        """
        if self.stream_tracks is None:
            raise MissingParameterError(name=_("stream tracks"))
        if self.media.subtitles is None:
            raise MissingParameterError(name=_("media subtitles"))

        track_index = self.stream_tracks[0]
        current = next(
            (
                stream
                for stream in self.media.subtitles
                if stream.track_index == track_index
            ),
            None,
        )
        if current is None:
            raise SubtitlesError(msg=_("Subtitles index not included."))

        language_code: str | None = None

        if language is not None:
            language_code = self._parse_language(raw=language)

        if title is None and current.title is None and language_code is not None:
            title = self._process_subtitles_title(title=title, lang=language_code)

        self.subtitles = Subtitles(
            path=self.media.path,
            track_index=track_index,
            language=language_code,
            title=title,
            forced=forced,
            default=default,
            hearing_impaired=hearing_impaired,
            visual_impaired=visual_impaired,
        )

    @staticmethod
    def to_subtitles_metadata_cmd(subtitles: Subtitles) -> list[str]:
        """Compone los flags -metadata y -disposition de la pista de subtítulos.

        Ffmpeg numera los streams del especificador `s:N` por tipo de pista,
        por lo que se usa el índice local (`track_index`), no el global.
        La opción `-metadata` exige la forma completa `<tipo>:<tipo>:<índice>`
        (`s:s:N`); `-c` y `-disposition` sí aceptan `s:N`.

        Args:
            subtitles: Modelo de metadatos de la pista de subtítulos.

        Returns:
            Flags `-metadata` y `-disposition` para el consumo de ffmpeg.

        Raises:
            MissingParameterError: Si la pista no tiene `track_index`.
        """
        if subtitles.track_index is None:
            raise MissingParameterError(name="subtitles.track_index")

        metadata: list[str] = []

        if subtitles.language:
            metadata.append(f"-metadata:s:s:{subtitles.track_index}")
            metadata.append(f"language={subtitles.language}")
        if subtitles.title:
            metadata.append(f"-metadata:s:s:{subtitles.track_index}")
            metadata.append(f"title={subtitles.title}")
        # Sin flags explícitos no se emiten disposiciones para no borrar
        # las que ya tenga la pista en el contenedor original.
        if any(
            field is not None
            for field in (
                subtitles.forced,
                subtitles.default,
                subtitles.hearing_impaired,
                subtitles.visual_impaired,
            )
        ):
            names = _disposition_names(subtitles)
            metadata.append(f"-disposition:s:{subtitles.track_index}")
            metadata.append("+".join(names) if names else "0")

        return metadata

    def to_exclusive_default_cmd(self) -> list[str]:
        """Retira la disposición `default` del resto de pistas de subtítulos.

        Se invoca cuando la pista en edición se marca como `default`: como
        `-disposition` reemplaza el conjunto completo de disposiciones, el
        valor de cada pista afectada se reconstruye conservando sus otros
        flags.

        Returns:
            Flags `-disposition` para las demás pistas marcadas como default,
            o una lista vacía si la pista editada no es default.

        Raises:
            MissingParameterError: Si la pista en edición no tiene
                `track_index`.
        """
        subtitles = self.subtitles
        if subtitles is None or not subtitles.default:
            return []
        if subtitles.track_index is None:
            raise MissingParameterError(name="subtitles.track_index")
        if self.media.subtitles is None:
            return []

        flags: list[str] = []
        for track in self.media.subtitles:
            if track.track_index is None:
                continue
            if track.track_index == subtitles.track_index or not track.default:
                continue
            remaining = [
                name for name in _disposition_names(track) if name != "default"
            ]
            flags.append(f"-disposition:s:{track.track_index}")
            flags.append("+".join(remaining) if remaining else "0")
        return flags

    def _process_codec(self) -> str:
        """Devuelve el códec de subtítulos del contenedor de salida."""
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
            + len(media.subtitles or [])
        )

    @staticmethod
    def _process_subtitles_index(media: Media) -> int:
        """Calcula el próximo índice local de subtítulo (s:N) libre en el output."""
        return len(media.subtitles) if media.subtitles is not None else 0

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


def _disposition_names(subtitles: Subtitles) -> list[str]:
    """Nombres de disposición activos en el modelo de subtítulos."""
    return [
        name
        for field, name in (
            (subtitles.forced, "forced"),
            (subtitles.default, "default"),
            (subtitles.hearing_impaired, "hearing_impaired"),
            (subtitles.visual_impaired, "visual_impaired"),
        )
        if field
    ]
