"""Mixin para operaciones con pistas de audio."""

import dataclasses
from dataclasses import dataclass
from pathlib import Path

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.language_codes import LANGUAGES, resolve_language
from pymedia.errors import InvalidCodecContainerError, MissingParameterError, UserError
from pymedia.ffprobe import get_audio_information
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.models.audio import Audio, AudioMetadata
from pymedia.models.media import Media


@dataclass(kw_only=True)
class AudioInputMixin:
    """Mixin para la recepción de ficheros de audio.

    Attributes:
        audio: Lista de pistas de audio importadas.
    """

    media: Media | None = None
    stream_tracks: list[int] | None = None
    audio: list[Audio] | None = None

    def create_add_audio(self, audio_input: Path, logger: Logger) -> None:
        """Añade pistas de audio a un contenedor multimedia.

        Args:
            audio_input: Ruta al fichero de audio a procesar.
            logger: Interfaz principal de la aplicación para generar mensajes.
        """
        media = self.media
        if media is None:
            raise MissingParameterError(name="media")

        audio_info: list[Audio] = get_audio_information(
            audio_input=audio_input, logger=logger
        )

        audio_tracks: list[Audio] = []
        for i, track in enumerate(audio_info):
            new_track = dataclasses.replace(
                track,
                path=audio_input.absolute(),
                global_index=self._process_stream_index(media=media) + i,
                track_index=self._process_audio_index(media=media) + i,
            )
            audio_tracks.append(new_track)

        self.audio = audio_tracks

    def validate_audio_containers(self, extension: str) -> None:
        """Valida la compatibilidad de códecs de audio importados con el contenedor.

        Args:
            extension: Extensión del contenedor de salida (ej. ".mp4", ".mkv").

        Raises:
            InvalidCodecContainerError: Si algún códec no es compatible
                con el contenedor.
        """
        if self.audio is None:
            return

        for track in self.audio:
            if track.codec is None:
                continue
            codec_data = AUDIO_CODECS.get(track.codec)
            if codec_data is None:
                continue
            if extension not in codec_data.containers:
                raise InvalidCodecContainerError(
                    extension=extension,
                    codec=codec_data.name,
                    supported=codec_data.containers,
                )

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


# Mapping de campos de AudioMetadata a flags de disposición de ffmpeg
_DISPOSITION_FIELD_TO_FLAG = {
    "default": "default",
    "forced": "forced",
    "hearing_impaired": "hearing_impaired",
    "commentary": "comment",
    "dubbed": "dub",
    "original": "original",
    "lyrics": "lyrics",
    "karaoke": "karaoke",
    "visual_impaired": "visual_impaired",
    "clean_effects": "clean_effects",
}


@dataclass(kw_only=True)
class AudioMetadataMixin:
    """Mixin para la manipulación de metadatos de audio.

    Attributes:
        language: Código ISO 639-2 del idioma de la pista.
        title: Título descriptivo de la pista.
        default: Se establece como la pista de audio por defecto del contenedor.
        forced: Fuerza al reproductor a usar la pista de audio.
        hearing_impaired: Pista orientada a personas con problemas auditivos.
        commentary: Pista de comentarios de audio.
        disposition_touched: Indica si el usuario modificó alguna disposición.
    """

    media: Media | None = None
    stream_tracks: list[int] | None = None

    language: str | None = None
    title: str | None = None
    default: bool | None = None
    forced: bool | None = None
    hearing_impaired: bool | None = None
    commentary: bool | None = None
    disposition_touched: bool = False

    def _find_audio_track(self, track_index: int) -> Audio:
        """Busca una pista de audio por su track_index local."""
        if self.media is None:
            raise MissingParameterError(name="media")
        if self.media.audio is None:
            raise MissingParameterError(name="media.audio")

        for track in self.media.audio:
            if track.track_index == track_index:
                return track

        raise UserError(msg=_("Audio index not included."))

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
            UserError: Si el idioma indicado no sigue el estándar ISO 639-2.
            MissingParameterError: Si no se recibió el listado de pistas o los
                metadatos del medio.
        """
        if self.stream_tracks is None:
            raise MissingParameterError(name="stream_tracks")
        if self.media is None:
            raise MissingParameterError(name="media")
        if self.media.audio is None:
            raise MissingParameterError(name="media.audio")

        track_index: int = self.stream_tracks[0]
        audio_track = self._find_audio_track(track_index)
        metadata: AudioMetadata = audio_track.metadata

        user_passed_title = title is not None

        if language is not None:
            metadata.language = self._parse_language(language)
            # Auto-título solo si el usuario pasó --language, no pasó --title,
            # y la pista no tiene título
            if not user_passed_title and metadata.title is None:
                lang_code = metadata.language
                if lang_code and lang_code in LANGUAGES:
                    metadata.title = LANGUAGES[lang_code].native

        if title is not None:
            metadata.title = title

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
        if commentary is not None:
            metadata.commentary = commentary
            self.commentary = commentary
            self.disposition_touched = True

    def to_audio_metadata_cmd(self, audio: Audio) -> list[str]:
        """Compone los flags -metadata y -disposition de la pista de audio.

        FFmpeg numera los streams del especificador `a:N` por tipo de pista,
        por lo que se usa el índice local (`track_index`), no el global.
        La opción `-metadata` exige la forma completa `<tipo>:<tipo>:<índice>`
        (`a:a:N`); `-disposition` sí acepta `a:N`.

        Args:
            audio: Modelo de metadatos de la pista de audio.

        Returns:
            Flags `-metadata` y `-disposition` para el consumo de ffmpeg.

        Raises:
            MissingParameterError: Si la pista no tiene `track_index`.
        """
        if audio.track_index is None:
            raise MissingParameterError(name="audio.track_index")

        metadata: list[str] = []

        meta: AudioMetadata = audio.metadata

        if meta.language:
            metadata.append(f"-metadata:s:a:{audio.track_index}")
            metadata.append(f"language={meta.language}")

        if meta.title:
            metadata.append(f"-metadata:s:a:{audio.track_index}")
            metadata.append(f"title={meta.title}")

        # Emitir -disposition solo si el usuario tocó alguna disposición
        if self.disposition_touched:
            names = self._disposition_names(audio)
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

        Raises:
            MissingParameterError: Si la pista en edición no tiene
                `track_index`.
        """
        if self.stream_tracks is None:
            raise MissingParameterError(name="stream_tracks")
        if self.media is None:
            raise MissingParameterError(name="media")
        if self.media.audio is None:
            raise MissingParameterError(name="media.audio")

        stream_track = self.stream_tracks[0]
        audio = self._find_audio_track(stream_track)

        if not audio.metadata.default:
            return []

        flags: list[str] = []

        for track in self.media.audio:
            if track.track_index is None:
                continue

            if track.track_index == audio.track_index:
                continue

            # Solo afectar a pistas que tengan default=True
            if not track.metadata.default:
                continue

            remaining = [
                flag
                for field, flag in _DISPOSITION_FIELD_TO_FLAG.items()
                if getattr(track.metadata, field) and flag != "default"
            ]

            flags.append(f"-disposition:a:{track.track_index}")
            flags.append("+".join(remaining) if remaining else "0")

        return flags

    @staticmethod
    def _parse_language(raw: str) -> str:
        """Resuelve el idioma al código ISO 639-2 correspondiente."""
        lang = resolve_language(raw)

        if lang is not None:
            return lang.iso_639_2_code

        raise UserError(
            msg=_(
                "Value doesn't match a native language name, "
                "an English language name, or a standard ISO 639-1/639-2 code: "
                "[https://www.loc.gov/standards/iso639-2/php/code_list.php]"
            )
        )

    def _disposition_names(self, audio: Audio) -> list[str]:
        """Nombres de disposición activos en el modelo de audio (10 campos)."""
        meta = audio.metadata
        return [
            flag
            for field, flag in _DISPOSITION_FIELD_TO_FLAG.items()
            if getattr(meta, field)
        ]
