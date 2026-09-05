"""Subcomando `info`: muestra los metadatos de un vídeo en una tabla Rich."""

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from pymedia.errors import (
    MissingParameterError,
)
from pymedia.locale_manager import locale_manager
from pymedia.locales import _  # noqa
from pymedia.models.media import Audio, Media, Subtitle, Video
from pymedia.models.parameters import InfoParameters
from pymedia.pipeline import BasePipeline
from pymedia.utils import parse_quantity, parse_size, parse_timedelta


class InfoPipeline(BasePipeline[InfoParameters]):
    """Comando de CLI que imprime los metadatos de un vídeo de entrada."""

    def process_parameters(self, media_input: Path) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        params: InfoParameters = InfoParameters()
        params.create_media_input(media_input=media_input, logger=self.logger)
        self.params = params

    def process_cmd(self) -> None:
        """Construye y muestra el panel Rich con los metadatos del vídeo."""
        if self.params.media is None:
            raise MissingParameterError(name="media")

        panel = _build_info_panel(
            media=self.params.media,
            media_input=self.params.media.path,
            locale=locale_manager.detect_language(),
        )
        self.logger.print(panel)


def _build_info_panel(media: Media, media_input: Path, locale: str = "en") -> Panel:
    """Construye el panel Rich con los metadatos del vídeo."""
    panel_width = 80
    na = _("-")

    def _build_general_table() -> Table:
        """Construye la tabla de datos generales del vídeo."""
        table = Table(title=f"📁 {_('General')}", show_header=True, expand=True)
        table.add_column(header=_("Field"), style="bold", ratio=1)
        table.add_column(header=_("Value"), ratio=3)
        table.add_row(_("File"), media_input.name)
        table.add_row(_("Container"), media.format_name or na)
        table.add_row(
            _("Duration"),
            parse_timedelta(media.duration) if media.duration else na,
        )
        if media.size is not None:
            table.add_row(_("Size"), parse_size(size_bytes=media.size, locale=locale))
        return table

    def _build_video_table(video: Video) -> Table:
        """Construye la tabla de metadatos de la pista de vídeo."""
        table = Table(title=f"🎬 {_('Video')}", show_header=True, expand=True)
        table.add_column(header=_("Field"), style="bold", ratio=1)
        table.add_column(header=_("Value"), ratio=3)
        table.add_row(
            _("Codec"),
            f"{video.codec} ({video.profile})"
            if video.codec and video.profile
            else video.codec or na,
        )
        if video.width is None or video.height is None:
            raise MissingParameterError(name="video dimension")
        table.add_row(_("Resolution"), f"{video.width}x{video.height}")
        table.add_row(_("FPS"), str(video.fps) if video.fps else na)
        table.add_row(
            _("Bitrate"),
            _("%(bit_rate)s bps")
            % {"bit_rate": parse_quantity(value=video.bit_rate, locale=locale)}
            if video.bit_rate
            else na,
        )
        return table

    def _build_audio_table(audio: list[Audio]) -> Table:
        """Construye la tabla de metadatos de las pistas de audio."""
        table = Table(title=f"🎵 {_('Audio')}", expand=True)
        for column in (
            _("Codec"),
            _("Sample rate"),
            _("Channels"),
            _("Language"),
        ):
            table.add_column(header=column, ratio=1)
        for track in audio:
            table.add_row(
                track.codec or na,
                f"{track.sample_rate} Hz" if track.sample_rate else na,
                str(track.channels or na),
                track.language or na,
            )
        return table

    def _build_subtitles_table(subtitles: list[Subtitle]) -> Table:
        """Construye la tabla de metadatos de las pistas de subtítulos."""
        table = Table(title=f"💬 {_('Subtitles')}", expand=True)
        for column in (
            _("Language"),
            _("Title"),
            _("Forced"),
            _("Default"),
        ):
            table.add_column(header=column, ratio=1)
        for sub in subtitles:
            table.add_row(
                sub.language or na,
                sub.title or na,
                "✓" if sub.forced else "",
                "✓" if sub.default else "",
            )
        return table

    sections = [_build_general_table()]

    if media.video is not None:
        sections.append(_build_video_table(media.video))
    if media.audio:
        sections.append(_build_audio_table(media.audio))
    if media.subtitle:
        sections.append(_build_subtitles_table(media.subtitle))

    return Panel(
        renderable=Group(*sections),
        title=_("Metadata"),
        border_style="cyan",
        width=panel_width,
    )
