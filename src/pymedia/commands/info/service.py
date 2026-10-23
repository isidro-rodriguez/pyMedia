"""Comando ``info``: service."""

import math
from dataclasses import astuple

from rich import box
from rich.console import Group, RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from pymedia.commands.base.service import BaseService
from pymedia.commands.info.parameters import InfoParameters
from pymedia.errors import MissingParameterError
from pymedia.locale_manager import locale_manager
from pymedia.locales import translate as _
from pymedia.models.media import Audio, Media, Subtitles, Video
from pymedia.ui import console
from pymedia.utils import parse_quantity, parse_size, parse_timedelta

_MAX_PANEL_WIDTH = 120


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

        self.logger.print(_build_info_panel(self.params.media))


def _build_info_panel(media: Media) -> Panel:
    """Construye el panel con una sección por tipo de pista.

    Raises:
        MissingParameterError: Si falta alguna propiedad necesaria de las pistas.
    """
    tables = [_general_table(media)]
    if media.video is not None:
        tables.append(_video_table(media, media.video))
    if media.audio:
        tables.append(_audio_table(media.audio))
    if media.subtitles:
        tables.append(_subtitles_table(media.subtitles))
    # Una línea en blanco entre secciones.
    sections: list[RenderableType] = [tables[0]]
    for table in tables[1:]:
        sections.extend([Text(""), table])

    return Panel(
        Group(*sections),
        title=Text(f" {media.path.name} ", style="panel.title"),
        title_align="left",
        subtitle=Text(_("Metadata"), style="panel.subtitle"),
        subtitle_align="right",
        border_style="border",
        box=box.ROUNDED,
        padding=(0, 1),
        width=min(console.width, _MAX_PANEL_WIDTH),
    )


# =============================================================================
#  Celdas
# =============================================================================


def _na() -> Text:
    """Celda de valor desconocido."""
    return Text("—", style="table.na")


def _value(value: object | None) -> Text:
    """Celda con el valor, o la marca de desconocido si falta."""
    return Text(str(value)) if value not in (None, "") else _na()


def _check(flag: bool | None) -> Text:
    """Celda de disposición: marca si está activa, punto tenue si no."""
    return Text("✔", style="table.check") if flag else Text("·", style="table.na")


def _section(title: str, icon: str) -> Table:
    """Tabla de sección con el estilo común del panel."""
    return Table(
        title=Text.assemble((f"{icon} ", ""), (title, "heading")),
        title_justify="left",
        box=box.SIMPLE_HEAD,
        border_style="table.border",
        header_style="table.header",
        show_edge=False,
        expand=True,
        pad_edge=False,
    )


# =============================================================================
#  Secciones
# =============================================================================


def _general_table(media: Media) -> Table:
    """Tabla clave-valor con los datos generales y los metadatos del contenedor."""
    locale = locale_manager.detect_language()
    metadata = media.metadata
    table = _section(_("General"), "📁")
    table.show_header = False
    table.box = None
    table.expand = False
    table.add_column(style="table.label", no_wrap=True, min_width=14)
    table.add_column()

    table.add_row(_("File"), _value(media.path.name))
    table.add_row(_("Container"), _value(media.format.name))
    table.add_row(
        _("Duration"),
        _value(parse_timedelta(media.duration) if media.duration else None),
    )
    if media.format.size is not None:
        table.add_row(
            _("Size"), _value(parse_size(size_bytes=media.format.size, locale=locale))
        )
    if any(astuple(metadata)):
        table.add_section()
    for label, value in (
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
    ):
        if value is not None:
            table.add_row(label, _value(value))
    return table


def _video_table(media: Media, video: Video) -> Table:
    """Tabla de la pista de vídeo.

    Raises:
        MissingParameterError: Si la pista no tiene índice o dimensiones.
    """
    if video.track_index is None:
        raise MissingParameterError(name="track_index")
    if video.format.width is None or video.format.height is None:
        raise MissingParameterError(name=_("video dimensions"))

    table = _section(_("Video"), "🎬")
    for header, ratio in (
        (_("Track"), 1),
        (_("Codec"), 3),
        (_("Resolution"), 2),
        (_("FPS"), 1),
        (_("Bit rate"), 2),
    ):
        table.add_column(header=header, ratio=ratio)
    codec = video.format.codec
    if codec and video.format.profile:
        codec = f"{codec} ({video.format.profile})"
    table.add_row(
        Text(str(video.track_index), style="highlight"),
        _value(codec),
        _value(f"{video.format.width}×{video.format.height}"),
        _value(video.format.fps),
        _format_kbps(media.video_bit_rate),
    )
    return table


def _audio_table(audio: list[Audio]) -> Table:
    """Tabla compacta de las pistas de audio.

    Raises:
        MissingParameterError: Si alguna pista no tiene índice.
    """
    table = _section(_("Audio"), "🎵")
    for header, ratio, justify in (
        (_("Track"), 1, "left"),
        (_("Codec"), 2, "left"),
        (_("Sample"), 2, "left"),
        (_("Channels"), 2, "left"),
        (_("Lang"), 1, "left"),
        (_("Title"), 3, "left"),
        # Iniciales de Default, Forced, Hearing Impaired y Commentary.
        (_("Def"), 1, "center"),
        (_("For"), 1, "center"),
        (_("HI"), 1, "center"),
        (_("Com"), 1, "center"),
    ):
        table.add_column(header=header, ratio=ratio, justify=justify)

    for track in audio:
        if track.track_index is None:
            raise MissingParameterError(name="track_index")
        rate = track.format.sample_rate
        dispositions = track.dispositions
        table.add_row(
            Text(str(track.track_index), style="highlight"),
            _value(track.format.codec),
            _value(f"{rate} Hz" if rate else None),
            _value(track.format.channels),
            _value(track.metadata.language),
            _value(track.metadata.title),
            _check(dispositions.default),
            _check(dispositions.forced),
            _check(dispositions.hearing_impaired),
            _check(dispositions.commentary),
        )
    return table


def _subtitles_table(subtitles: list[Subtitles]) -> Table:
    """Tabla de las pistas de subtítulos.

    Raises:
        MissingParameterError: Si alguna pista no tiene índice.
    """
    table = _section(_("Subtitles"), "💬")
    for header, ratio, justify in (
        (_("Track"), 1, "left"),
        (_("Codec"), 2, "left"),
        (_("Language"), 2, "left"),
        (_("Title"), 3, "left"),
        # Iniciales de Default, Forced, Hearing Impaired y Visual Impaired.
        (_("Def"), 1, "center"),
        (_("For"), 1, "center"),
        (_("HI"), 1, "center"),
        (_("VI"), 1, "center"),
    ):
        table.add_column(header=header, ratio=ratio, justify=justify)

    for sub in subtitles:
        if sub.track_index is None:
            raise MissingParameterError(name="track_index")
        dispositions = sub.dispositions
        table.add_row(
            Text(str(sub.track_index), style="highlight"),
            _value(sub.format.codec),
            _value(sub.metadata.language),
            _value(sub.metadata.title),
            _check(dispositions.default),
            _check(dispositions.forced),
            _check(dispositions.hearing_impaired),
            _check(dispositions.visual_impaired),
        )
    return table


def _format_kbps(bit_rate: float | None) -> Text:
    """Formatea una tasa de bits en bps como kbps (SI), o desconocido si falta."""
    if bit_rate is None:
        return _na()
    kbps = parse_quantity(
        value=math.floor(bit_rate / 1000), locale=locale_manager.detect_language()
    )
    return Text(_("%(bit_rate)s kbps") % {"bit_rate": kbps})
