"""Mixin de opciones de remultiplexación."""

from dataclasses import dataclass

from pymedia.errors import MissingParameterError
from pymedia.models.media import Media


@dataclass(kw_only=True)
class FastStartMixin:
    """Mixin que mueve el índice del contenedor al inicio de la salida."""

    fast_start: bool

    @staticmethod
    def to_fast_start_cmd() -> list[str]:
        """Devuelve los argumentos que habilitan el índice al inicio del fichero.

        Returns:
            Argumentos `-movflags +faststart` para el consumo de ffmpeg.
        """
        return ["-movflags", "+faststart"]


@dataclass(kw_only=True)
class RegeneratePtsMixin:
    """Mixin que regenera los marcadores de tiempo corruptos del contenedor."""

    regenerate_pts: bool

    @staticmethod
    def to_regenerate_pts_cmd() -> list[str]:
        """Devuelve los argumentos que fuerzan la regeneración de los PTS.

        Returns:
            Argumentos `-fflags +genpts` para el consumo de ffmpeg.
        """
        return ["-fflags", "+genpts"]


@dataclass(kw_only=True)
class SortTracksMixin:
    """Mixin para ordenar las pistas del contenedor de salida.

    Attributes:
        sort_tracks: Habilita la ordenación de las pistas por tipo e idioma.
    """

    media: Media | None = None
    sort_tracks: bool

    def to_sort_tracks_cmd(self) -> list[str]:
        """Devuelve los `-map` que indican a ffmpeg el orden de las pistas.

        Returns:
            Lista de argumentos lista para el consumo de ffmpeg, o vacía si la
            ordenación está desactivada.
        """
        return self._build_sorted_tracks_map()

    def _build_sorted_tracks_map(self) -> list[str]:
        """Construye los `-map` que ordenan las pistas de la salida.

        Ordena primero vídeo, luego audio y por último subtítulos, colocando
        las pistas con idioma al inicio y ordenadas alfabéticamente por
        código; las pistas sin idioma conservan su orden original.
        """
        map_args: list[str] = []
        media = self.media
        if media is None:
            raise MissingParameterError(name="media")

        if media.video is not None:
            # Solo se soporta una pista de vídeo por contenedor.
            map_args.extend(["-map", f"0:v:{media.video.track_index}"])

        for tracks, kind in (
            (media.audio, "a"),
            (media.subtitles, "s"),
        ):
            if tracks is None:
                continue

            with_language = [track for track in tracks if track.language is not None]
            without_language = [track for track in tracks if track.language is None]
            with_language.sort(key=lambda track: (track.language or "").casefold())

            for track in with_language + without_language:
                map_args.extend(["-map", f"0:{kind}:{track.track_index}"])

        return map_args
