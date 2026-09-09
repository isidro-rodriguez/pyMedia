"""Mixin para operaciones con pistas de audio."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from pymedia.data.language_codes import LANGUAGES
from pymedia.errors import (
    AudioError,
    InvalidArgumentError,
    MissingArgumentError,
    MissingParameterError,
)
from pymedia.ffmpeg.probe import validate_audio_file_codec
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.models.audio import Audio
from pymedia.models.media import Media


class _AudioContext(Protocol):
    media: Media
    media_output: Path
    stream_tracks: list[int]


@dataclass(kw_only=True)
class AudioInputMixin(_AudioContext):
    """Mixin para la recepción de ficheros de audio.

    Attributes:
        audio: Objeto de metadatos para la pista de audio.
    """

    audio: Audio | None = None

    def create_add_audio(
        self,
        audio_input: Path,
        logger: Logger,
        language: str | None = None,
        title: str | None = None,
        default: bool = False,
        forced: bool = False,
        hearing_impaired: bool = False,
        commentary: bool = False,
    ) -> None:
        """Crea un modelo de metadatos de audio.

        El idioma debe indicarse mediante un código o nombre reconocido
        según ISO 639-2.

        Args:
            audio_input: Ruta al fichero de audio a procesar.
            language: Idioma de la pista de audio.
            logger: Interfaz principal de la aplicación para generar mensajes.
            title: Título descriptivo de la pista de audio.
            default: Si es la pista de audio por defecto del vídeo.
            forced: Si es una pista de audio forzada.
            hearing_impaired: Si está adaptada a personas con problemas auditivos.
            commentary: Si es una pista de comentarios de audio.

        Raises:
            InvalidArgumentError: Si el idioma indicado no sigue el estándar ISO 639-2.
            MissingArgumentError: Si no se recibió el argumento `language`.
        """
        if language is None:
            raise MissingArgumentError(name=_("audio language"))

        language_code = self._parse_language(raw=language)

        self.audio = Audio(
            path=audio_input.absolute(),
            global_index=self._process_stream_index(media=self.media),
            track_index=self._process_audio_index(media=self.media),
            codec=validate_audio_file_codec(audio_input=audio_input, logger=logger),
            language=language_code,
            title=self._process_audio_title(title=title, lang=language_code),
            default=default,
            forced=forced,
            hearing_impaired=hearing_impaired,
            commentary=commentary,
        )

    def create_edit_audio(
        self,
        language: str | None = None,
        title: str | None = None,
        default: bool | None = None,
        forced: bool | None = None,
        hearing_impaired: bool | None = None,
        commentary: bool | None = None,
    ) -> None:
        """Crea un modelo de metadatos de audio para editar una pista.

        Args:
            language: Idioma de la pista de audio.
            title: Título descriptivo de la pista de audio.
            default: Si es la pista de audio por defecto del vídeo.
            forced: Si es una pista de audio forzada.
            hearing_impaired: Si está adaptada a personas con problemas auditivos.
            commentary: Si es una pista de comentarios de audio.

        Raises:
            InvalidArgumentError: Si el idioma indicado no sigue el estándar ISO 639-2.
            MissingParameterError: Si no se recibió el listado de pistas o los
                metadatos del medio.
            AudioError: Si la pista indicada no existe en el contenedor.
        """
        if self.stream_tracks is None:
            raise MissingParameterError(name=_("stream tracks"))
        if self.media.audio is None:
            raise MissingParameterError(name=_("media audio"))

        track_index = self.stream_tracks[0]
        current = next(
            (
                stream
                for stream in self.media.audio
                if stream.track_index == track_index
            ),
            None,
        )

        if current is None:
            raise AudioError(msg=_("Audio index not included."))

        language_code: str | None = None

        if language is not None:
            language_code = self._parse_language(raw=language)

        if title is None and current.title is None and language_code is not None:
            title = self._process_audio_title(
                title=title,
                lang=language_code,
            )

        self.audio = Audio(
            path=self.media.path,
            track_index=track_index,
            language=language_code,
            title=title,
            default=default,
            forced=forced,
            hearing_impaired=hearing_impaired,
            commentary=commentary,
        )

    @staticmethod
    def to_audio_metadata_cmd(audio: Audio) -> list[str]:
        """Compone los flags -metadata y -disposition de la pista de audio.

        FFmpeg numera los streams del especificador `a:N` por tipo de pista,
        por lo que se usa el índice local (`track_index`), no el global.

        La opción `-metadata` exige la forma completa `<tipo>:<tipo>:<índice>`
        (`a:a:N`); `-disposition` sí acepta `a:N`.
        """
        if audio.track_index is None:
            raise MissingParameterError(name="audio.track_index")

        metadata: list[str] = []

        if audio.language:
            metadata.append(f"-metadata:s:a:{audio.track_index}")
            metadata.append(f"language={audio.language}")

        if audio.title:
            metadata.append(f"-metadata:s:a:{audio.track_index}")
            metadata.append(f"title={audio.title}")

        # Sin flags explícitos no se emiten disposiciones para no borrar
        # las que ya tenga la pista en el contenedor original.
        if any(
            field is not None
            for field in (
                audio.default,
                audio.forced,
                audio.hearing_impaired,
                audio.commentary,
            )
        ):
            names = _disposition_names(audio)
            metadata.append(f"-disposition:a:{audio.track_index}")
            metadata.append("+".join(names) if names else "0")

        return metadata

    def to_exclusive_default_cmd(self) -> list[str]:
        """Retira la disposición `default` del resto de pistas de audio.

        Se invoca cuando la pista en edición se marca como `default`.
        Como `-disposition` reemplaza el conjunto completo de disposiciones,
        el valor de cada pista afectada se reconstruye conservando sus otros
        flags.

        Returns:
            Flags `-disposition` para las demás pistas marcadas como default,
            o una lista vacía si la pista editada no es default.
        """
        audio = self.audio

        if audio is None or not audio.default:
            return []

        if audio.track_index is None:
            raise MissingParameterError(name="audio.track_index")

        if self.media.audio is None:
            return []

        flags: list[str] = []

        for track in self.media.audio:
            if track.track_index is None:
                continue

            if track.track_index == audio.track_index or not track.default:
                continue

            remaining = [
                name for name in _disposition_names(track) if name != "default"
            ]

            flags.append(f"-disposition:a:{track.track_index}")
            flags.append("+".join(remaining) if remaining else "0")

        return flags

    @staticmethod
    def _process_stream_index(media: Media) -> int:
        """Calcula el índice absoluto que ocupará el nuevo audio en el output."""
        return (
            (1 if media.video is not None else 0)
            + len(media.audio or [])
            + len(media.subtitles or [])
        )

    @staticmethod
    def _process_audio_index(media: Media) -> int:
        """Calcula el próximo índice local de audio (`a:N`) libre en el output."""
        return len(media.audio) if media.audio is not None else 0

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
    def _process_audio_title(title: str | None, lang: str) -> str:
        """Utiliza el nombre del idioma como título si no se ha indicado."""
        if title is not None:
            return title

        return LANGUAGES[lang].native_name


def _disposition_names(audio: Audio) -> list[str]:
    """Nombres de disposición activos en el modelo de audio."""
    return [
        name
        for field, name in (
            (audio.default, "default"),
            (audio.forced, "forced"),
            (audio.hearing_impaired, "hearing_impaired"),
            (audio.commentary, "comment"),
        )
        if field
    ]
