"""Subcomando `info`: muestra los metadatos de un vídeo en una tabla Rich."""

from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from pymedia.errors import (
    MissingMediaError,
    MissingParameterError,
)
from pymedia.locale_manager import locale_manager
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.models.media import Audio, Media, Subtitle, Video
from pymedia.models.pipeline.info_pipeline import InfoArguments, InfoParameters
from pymedia.pipeline.base_pipeline import SinglePipeline
from pymedia.typer.options import (
    DebugOption,
    HelpOption,
    InputSingleArgument,
)
from pymedia.utils import parse_quantity, parse_size, parse_timedelta


class InfoCommand(SinglePipeline[InfoArguments, InfoParameters]):
    """Comando de CLI que imprime los metadatos de un vídeo de entrada."""

    command_name = "info"

    @staticmethod
    def cli(
        input_single: InputSingleArgument,
        debug: DebugOption = False,
        help_: HelpOption = False,
    ) -> None:
        """Punto de entrada de Typer: construye los argumentos y ejecuta el comando.

        Args:
            input_single: Vídeo del que se muestran los metadatos.
            debug: Habilita el nivel de log DEBUG.
            help_: Muestra la ayuda del comando.
        """
        InfoCommand.run(
            args=InfoCommand.build_args(
                args_cls=InfoArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self) -> None:
        """Valida y parsea los argumentos en parámetros procesados."""
        self.params = InfoParameters.create(args=self.args, logger=self.logger)

    def process_cmd(self) -> None:
        """Construye y muestra el panel Rich con los metadatos del vídeo."""
        if self.params.input_single is None:
            raise MissingParameterError(name="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))

        panel = _build_info_panel(
            media=self.params.media,
            single_input=self.params.input_single,
            locale=locale_manager.detect_language(),
        )
        self.logger.print(panel)

    @classmethod
    def run(cls, args: InfoArguments, debug: bool) -> None:
        """Ejecuta el flujo del comando Info sin generar comandos ffmpeg.

        Args:
            args: Argumentos tipados del comando Info.
            debug: Habilita el nivel de log DEBUG.
        """
        config = Config.load()
        cls.logger = Logger.load(debug=debug)
        instance = cls(args, config)
        instance.process_parameters()
        instance.process_cmd()


def _build_info_panel(media: Media, single_input: Path, locale: str = "en") -> Panel:
    """Construye el panel Rich con los metadatos del vídeo."""
    panel_width = 80
    na = _("-")

    def _build_general_table() -> Table:
        """Construye la tabla de datos generales del vídeo."""
        table = Table(title=f"📁 {_('General')}", show_header=True, expand=True)
        table.add_column(_("Field"), style="bold", ratio=1)
        table.add_column(_("Value"), ratio=3)
        table.add_row(_("File"), single_input.name)
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
        table.add_column(_("Field"), style="bold", ratio=1)
        table.add_column(_("Value"), ratio=3)
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
    if media.subtitles:
        sections.append(_build_subtitles_table(media.subtitles))

    return Panel(
        renderable=Group(*sections),
        title=_("Metadata"),
        border_style="cyan",
        width=panel_width,
    )
