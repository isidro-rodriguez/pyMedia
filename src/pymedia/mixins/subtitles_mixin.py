"""Mixin para operaciones con subtítulos."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.data.language_codes import LANGUAGES, resolve_language
from pymedia.errors import (
    MissingParameterError,
    UserError,
)
from pymedia.ffprobe import validate_subtitles_file_codec
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.models.media import Media
from pymedia.models.subtitles import (
    Subtitles,
    SubtitlesDispositions,
    SubtitlesFormat,
    SubtitlesMetadata,
)


@dataclass(kw_only=True)
class SubtitlesInputMixin:
    """Mixin para la recepción de ficheros de subtítulos.

    Attributes:
        subtitles: Objeto de metadatos para subtítulos.
    """

    media: Media | None = None
    media_output: Path | None = None
    stream_tracks: list[int] | None = None
    subtitles: Subtitles | None = None

    def create_add_subtitles(
        self,
        subtitles_input: Path,
        logger: Logger,
        language: str,
        title: str | None = None,
    ) -> None:
        """Crea un modelo de metadatos de subtítulos.

        Modelo de metadatos que fuerza a indicar un código de idioma, según ISO 639-2, y
        genera el nombre nativo como título si no se ha aportado ninguno.

        Args:
            subtitles_input: Ruta del fichero de subtítulo a procesar.
            language: Lenguaje del fichero de subtítulos.
            logger: Interfaz principal de la aplicación para generar mensajes.
            title: Título descriptivo de la pista de subtítulos.

        Raises:
            InvalidArgumentError: Si el idioma indicado no sigue el estándar ISO 639-2.
            MissingArgumentError: Si no se recibió el argumento `language`.
            SubtitlesError: Si el contenedor de salida no tiene un códec de
                subtítulos soportado.
        """

        def _process_stream_index() -> int:
            """Calcula el índice que ocupará el nuevo subtítulo en la salida."""
            if self.media is None:
                raise MissingParameterError(name="media")
            return (
                (1 if self.media.video is not None else 0)
                + len(self.media.audio or [])
                + len(self.media.subtitles or [])
            )

        if self.media is None:
            raise MissingParameterError(name="media")

        validate_subtitles_file_codec(subtitles_input=subtitles_input, logger=logger)
        language_code = _parse_language(raw=language)
        subtitles = self.media.subtitles
        self.subtitles = Subtitles(
            path=subtitles_input.absolute(),
            global_index=_process_stream_index(),
            track_index=len(subtitles) if subtitles is not None else 0,
            format=SubtitlesFormat(codec=self._process_codec()),
            metadata=SubtitlesMetadata(
                language=language_code,
                title=_process_subtitles_title(title=title, lang=language_code),
            ),
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

        if subtitles.metadata.language:
            metadata.append(f"-metadata:s:s:{subtitles.track_index}")
            metadata.append(f"language={subtitles.metadata.language}")
        if subtitles.metadata.title:
            metadata.append(f"-metadata:s:s:{subtitles.track_index}")
            metadata.append(f"title={subtitles.metadata.title}")

        return metadata

    def _process_codec(self) -> str:
        """Devuelve el códec de subtítulos del contenedor de salida."""
        if self.media_output is None:
            raise MissingParameterError(name="media_output")
        match self.media_output.suffix:
            case ".m2ts" | ".mov" | ".mp4" | ".ts":
                return "mov_text"
            case ".mkv":
                return "srt"
            case ".webm":
                return "webvtt"
            case _:
                raise UserError(msg=_("Subtitles codec not supported."))


# Mapping de campos de SubtitlesMetadata a flags de disposición de ffmpeg
_DISPOSITION_FIELD_TO_FLAG = {
    "default": "default",
    "forced": "forced",
    "hearing_impaired": "hearing_impaired",
    "visual_impaired": "visual_impaired",
}


@dataclass(kw_only=True)
class SubtitlesMetadataMixin:
    """Mixin para la manipulación de metadatos de subtítulos.

    Attributes:
        language: Código ISO 639-2 del idioma de la pista.
        title: Título descriptivo de la pista.
        forced: Fuerza al reproductor a usar la pista de subtítulos.
        default: Se establece como la pista de subtítulos por defecto del contenedor.
        hearing_impaired: Pista orientada a personas con problemas auditivos.
        visual_impaired: Pista orientada a personas con problemas visuales.
        disposition_touched: Indica si el usuario modificó alguna disposición.
    """

    media: Media | None = None
    stream_tracks: list[int] | None = None
    subtitles: Subtitles | None = None

    language: str | None = None
    title: str | None = None
    forced: bool | None = None
    default: bool | None = None
    hearing_impaired: bool | None = None
    visual_impaired: bool | None = None
    disposition_touched: bool = False

    def create_edit_subtitles(
        self,
        language: str | None = None,
        title: str | None = None,
        forced: bool | None = None,
        default: bool | None = None,
        hearing_impaired: bool | None = None,
        visual_impaired: bool | None = None,
    ) -> None:
        """Crea un modelo de metadatos de subtítulos para editar una pista.

        Args:
            language: Idioma de la pista de subtítulos.
            title: Título descriptivo de la pista de subtítulos.
            forced: Si es una pista de subtítulos forzada.
            default: Si es la pista de subtítulos por defecto del vídeo.
            hearing_impaired: Si está adaptada a personas con problemas auditivos.
            visual_impaired: Si está adaptada a personas con problemas visuales.

        Raises:
            UserError: Si el idioma indicado no sigue el estándar ISO 639-2.
            MissingParameterError: Si no se recibió el listado de pistas o los
                metadatos del medio.
        """
        if self.stream_tracks is None:
            raise MissingParameterError(name="stream_tracks")
        if self.media is None:
            raise MissingParameterError(name="media")
        if self.media.subtitles is None:
            raise MissingParameterError(name="media.subtitles")

        track_index: int = self.stream_tracks[0]
        track = _find_subtitles_track(media=self.media, track_index=track_index)
        metadata: SubtitlesDispositions = track.dispositions

        if language is not None:
            language_code = _parse_language(language)
            track.metadata.language = language_code
            if title is None and track.metadata.title is None:
                if language_code in LANGUAGES:
                    track.metadata.title = LANGUAGES[language_code].native

        if title is not None:
            track.metadata.title = title

        if default is not None:
            metadata.default = default
            self.default = default
            self.disposition_touched = True
        if forced is not None:
            metadata.forced = forced
            self.forced = forced
            self.disposition_touched = True
        if hearing_impaired is not None:
            metadata.hearing_impaired = hearing_impaired
            self.hearing_impaired = hearing_impaired
            self.disposition_touched = True
        if visual_impaired is not None:
            metadata.visual_impaired = visual_impaired
            self.visual_impaired = visual_impaired
            self.disposition_touched = True

        self.subtitles = track

    def to_subtitles_metadata_cmd(self, subtitles: Subtitles) -> list[str]:
        """Compone los flags -metadata y -disposition de la pista de subtítulos.

        FFmpeg numera los streams del especificador `s:N` por tipo de pista,
        por lo que se usa el índice local (`track_index`), no el global.
        La opción `-metadata` exige la forma completa `<tipo>:<tipo>:<índice>`
        (`s:s:N`); `-disposition` sí acepta `s:N`.

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

        if subtitles.metadata.language:
            metadata.append(f"-metadata:s:s:{subtitles.track_index}")
            metadata.append(f"language={subtitles.metadata.language}")

        if subtitles.metadata.title:
            metadata.append(f"-metadata:s:s:{subtitles.track_index}")
            metadata.append(f"title={subtitles.metadata.title}")

        # Emitir -disposition solo si el usuario tocó alguna disposición
        if self.disposition_touched:
            names = _disposition_names(subtitles)
            metadata.append(f"-disposition:s:{subtitles.track_index}")
            metadata.append("+".join(names) if names else "0")

        return metadata

    def to_exclusive_default_cmd(self) -> list[str]:
        """Retira la disposición `default` del resto de pistas de subtítulos.

        Se invoca cuando la pista en edición se marca como `default`.
        Como `-disposition` reemplaza el conjunto completo de disposiciones,
        el valor de cada pista afectada se reconstruye conservando sus otros
        flags.

        Returns:
            Flags `-disposition` para las demás pistas marcadas como default,
            o una lista vacía si la pista editada no es default.

        Raises:
            MissingParameterError: Si la pista en edición no tiene
                `track_index`.
        """
        if self.stream_tracks is None:
            raise MissingParameterError(name="stream_tracks")
        if self.media is None:
            raise MissingParameterError(name="media")
        if self.media.subtitles is None:
            raise MissingParameterError(name="media.subtitles")

        stream_track = self.stream_tracks[0]
        subtitles = _find_subtitles_track(media=self.media, track_index=stream_track)

        if not subtitles.dispositions.default:
            return []

        flags: list[str] = []

        for track in self.media.subtitles:
            if track.track_index is None:
                continue

            if track.track_index == subtitles.track_index:
                continue

            # Solo afectar a pistas que tengan default=True
            if not track.dispositions.default:
                continue

            remaining = [
                flag
                for field, flag in _DISPOSITION_FIELD_TO_FLAG.items()
                if getattr(track.dispositions, field) and flag != "default"
            ]

            flags.append(f"-disposition:s:{track.track_index}")
            flags.append("+".join(remaining) if remaining else "0")

        return flags


def _disposition_names(subtitles: Subtitles) -> list[str]:
    """Nombres de disposición activos en el modelo de subtítulos."""
    dispositions = subtitles.dispositions
    return [
        name
        for field, name in (
            (dispositions.forced, "forced"),
            (dispositions.default, "default"),
            (dispositions.hearing_impaired, "hearing_impaired"),
            (dispositions.visual_impaired, "visual_impaired"),
        )
        if field
    ]


def _find_subtitles_track(media: Media, track_index: int) -> Subtitles:
    """Busca una pista de subtítulos por su track_index local."""
    if media.subtitles is None:
        raise MissingParameterError(name="media.subtitles")

    for track in media.subtitles:
        if track.track_index == track_index:
            return track

    raise UserError(msg=_("Subtitles index not included."))


def _parse_language(raw: str) -> str:
    """Resuelve el idioma al código ISO 639-2 correspondiente."""
    lang = resolve_language(raw)
    if lang is not None:
        return lang.iso_639_2_code
    raise UserError(
        msg=_(
            "Value doesn't match with ISO 639-1/639-2: "
            "Codes for the Representation of Names of Languages."
            "[https://www.loc.gov/standards/iso639-2/php/code_list.php]"
        )
    )


def _process_subtitles_title(title: str | None, lang: str) -> str:
    """Utiliza el nombre del idioma como título si no lo ha indicado el usuario."""
    if title is not None:
        return title
    return LANGUAGES[lang].native
