"""Comando ``info``: service."""

import math
from dataclasses import astuple

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from pymedia.commands.base_service import BaseService
from pymedia.commands.info.parameters import InfoParameters
from pymedia.errors import MissingParameterError
from pymedia.locale_manager import locale_manager
from pymedia.locales import translate as _
from pymedia.models.audio import get_audio_metadata
from pymedia.models.media import Audio, Subtitles, Video
from pymedia.models.subtitles import get_subtitles_metadata
from pymedia.utils import parse_quantity, parse_size, parse_timedelta

_PANEL_WIDTH = 120


class InfoService(BaseService[InfoParameters]):
    """Comando de CLI que imprime los metadatos de un vídeo de entrada."""

    def start(self) -> None:
        """Construye y muestra el panel Rich con los metadatos del vídeo.

        Raises:
            MissingParameterError: Si el medio no se obtuvo o falta alguna
                propiedad técnica necesaria para pintar la tabla.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        panel = self._build_info_panel()
        self.logger.print(panel)

    def _build_info_panel(self) -> Panel:
        """Construye el panel Rich con los metadatos del vídeo."""
        if self.params.media is None:
            raise MissingParameterError(name="media")
        media = self.params.media
        media_input = media.path
        locale = locale_manager.detect_language()
        na = _("-")

        def _build_general_table() -> Table:
            """Construye la tabla de datos generales del vídeo."""
            if media.metadata is None:
                raise MissingParameterError(name="media.metadata")
            metadata = media.metadata

            metadata_fields = (
                (_("Title"), metadata.title),
                (_("Comment"), metadata.comment),
                (_("Description"), metadata.description),
                (_("Synopsis"), metadata.synopsis),
                (_("Genre"), metadata.genre),
                (_("Date"), metadata.date),
                (_("Copyright"), metadata.copyright),
                (_("Law rating"), metadata.law_rating),
                (_("Artist"), metadata.artist),
                (_("Album"), metadata.album),
                (_("Encoder"), metadata.encoder),
            )

            table = Table(title=f"📁 {_('General')}", show_header=True, expand=True)
            table.add_column(header=_("Field"), style="bold", ratio=1)
            table.add_column(header=_("Value"), ratio=3)
            table.add_row(_("File"), media_input.name)
            table.add_row(_("Container"), media.format_name or na)
            table.add_row(
                _("Duration"),
                parse_timedelta(media.duration) if media.duration else na,
                end_section=True
                if any(astuple(metadata)) and media.size is None
                else False,
            )
            if media.size is not None:
                table.add_row(
                    _("Size"),
                    parse_size(size_bytes=media.size, locale=locale),
                    end_section=True if any(astuple(metadata)) else False,
                )
            for label, value in metadata_fields:
                if value is not None:
                    table.add_row(label, str(value) or na)

            return table

        def _build_video_table(video: Video) -> Table:
            """Construye la tabla de metadatos de la pista de vídeo."""
            if video.global_index is None:
                raise MissingParameterError(name="global_index")
            if video.track_index is None:
                raise MissingParameterError(name="track_index")
            if video.width is None or video.height is None:
                raise MissingParameterError(name=_("video dimensions"))

            table = Table(title=f"🎬 {_('Video')}", show_header=True, expand=True)
            table.add_column(header=_("Track"), ratio=1, justify="center")
            table.add_column(header=_("Codec"), ratio=2, justify="center")
            table.add_column(header=_("Resolution"), ratio=2, justify="center")
            table.add_column(header=_("FPS"), ratio=1, justify="center")
            table.add_column(header=_("Bit rate"), ratio=1, justify="center")
            table.add_row(
                str(video.track_index),
                f"{video.codec} ({video.profile})"
                if video.codec and video.profile
                else video.codec or na,
                f"{video.width}x{video.height}",
                str(video.fps) if video.fps else na,
                self._estimated_bit_rate(),
            )
            return table

        def _build_audio_table(audio: list[Audio]) -> Table:
            """Construye la tabla compacta de metadatos de las pistas de audio."""
            table = Table(title=f"🎵 {_('Audio')}", expand=True)
            table.add_column(header=_("Track"), ratio=1, justify="center")
            table.add_column(header=_("Codec"), ratio=1, justify="center")
            table.add_column(header=_("Sample"), ratio=1, justify="center")
            table.add_column(header=_("Channels"), ratio=1, justify="center")
            table.add_column(header=_("Lang"), ratio=1, justify="center")
            table.add_column(header=_("Title"), ratio=2, justify="center")
            # Inciales de "Default" para mantener tabla compacta
            table.add_column(header=_("Def"), ratio=1, justify="center")
            # Iniciales de "Forced"
            table.add_column(header=_("For"), ratio=1, justify="center")
            # Iniciales de Hearing Impaired
            table.add_column(header=_("HI"), ratio=1, justify="center")
            # Iniciales de Commentary
            table.add_column(header=_("Com"), ratio=1, justify="center")

            for track in audio:
                if track.track_index is None:
                    raise MissingParameterError(name="track_index")

                meta = get_audio_metadata(track)

                table.add_row(
                    str(track.track_index),
                    track.codec or na,
                    f"{track.sample_rate} Hz" if track.sample_rate else na,
                    str(track.channels or na),
                    meta.language or na,
                    meta.title or na,
                    "✓" if meta.default else "",
                    "✓" if meta.forced else "",
                    "✓" if meta.hearing_impaired else "",
                    "✓" if meta.commentary else "",
                )

            return table

        def _build_subtitles_table(subtitles: list[Subtitles]) -> Table:
            """Construye la tabla de metadatos de las pistas de subtítulos."""
            table = Table(title=f"💬 {_('Subtitles')}", expand=True)
            table.add_column(header=_("Track"), ratio=1, justify="center")
            table.add_column(header=_("Codec"), ratio=2, justify="center")
            table.add_column(header=_("Language"), ratio=2, justify="center")
            table.add_column(header=_("Title"), ratio=2, justify="center")
            # Iniciales de "Default"
            table.add_column(header=_("Def"), ratio=1, justify="center")
            # Iniciales de "Forced"
            table.add_column(header=_("For"), ratio=1, justify="center")
            # Iniciales de "Hearing Impaired"
            table.add_column(header=_("HI"), ratio=1, justify="center")
            # Iniciales de "Visual Impaired"
            table.add_column(header=_("VI"), ratio=1, justify="center")
            for sub in subtitles:
                if sub.track_index is None:
                    raise MissingParameterError(name="track_index")

                meta = get_subtitles_metadata(sub)

                table.add_row(
                    str(sub.track_index),
                    sub.codec or na,
                    meta.language or na,
                    meta.title or na,
                    "✓" if meta.default else "",
                    "✓" if meta.forced else "",
                    "✓" if meta.hearing_impaired else "",
                    "✓" if meta.visual_impaired else "",
                )
            return table

        sections = [_build_general_table()]

        if media.video is not None:
            sections.append(_build_video_table(media.video))
        if media.audio:
            sections.append(_build_audio_table(media.audio))
        if media.subtitles:
            sections.append(_build_subtitles_table(media.subtitles))

        return Panel(
            renderable=Group(*sections),
            title=_("Metadata"),
            border_style="cyan",
            width=_PANEL_WIDTH,
        )

    def _estimated_bit_rate(self) -> str:
        """Devuelve el bit_rate obtenido por ffprobe o lo calcula si no se obtuvo."""
        if self.params.media is None:
            raise MissingParameterError(name="media")
        media = self.params.media
        if media.size is None:
            raise MissingParameterError(name="media")
        if media.duration is None:
            raise MissingParameterError(name="duration")
        video = self.params.media.video
        if video is None:
            raise MissingParameterError(name="video")

        locale = locale_manager.detect_language()

        if video.bit_rate:
            bit_rate = video.bit_rate / 1024
        else:
            bit_rate = (media.size * 8 / media.duration.total_seconds()) / 1024

        bit_rate = math.floor(bit_rate)
        bit_rate = parse_quantity(value=bit_rate, locale=locale)

        return _("%(bit_rate)s kbps") % {"bit_rate": bit_rate}
