from datetime import timedelta
from pathlib import Path

from rich.console import Group
from rich.panel import Panel
from rich.table import Table

from pymedia import locales
from pymedia.commands.base_command import SingleCommand
from pymedia.errors import (
    MissingMediaError,
    MissingParameterError,
)
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.models.media import Audio, Media, Subtitle, Video
from pymedia.models.pipeline.info_pipeline import InfoArguments, InfoParameters
from pymedia.services.locale_service import detect_language
from pymedia.typer_options import (
    DebugOption,
    HelpOption,
    InputSingleArgument,
)
from pymedia.utils import parse_quantity


class InfoCommand(SingleCommand[InfoArguments, InfoParameters]):
    name = "info"

    @staticmethod
    def cli(
        input_single: InputSingleArgument,
        debug: DebugOption = False,
        help_: HelpOption = False,
    ) -> None:
        InfoCommand.run(
            args=InfoCommand.build_args(
                args_cls=InfoArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self) -> None:
        self.params = InfoParameters.create(args=self.args, logger=self.logger)

    def process_cmd(self) -> None:
        if self.params.input_single is None:
            raise MissingParameterError(name="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))

        panel = _build_info_panel(
            media=self.params.media,
            single_input=self.params.input_single,
            locale=detect_language(),
        )
        self.logger.print(panel)

    @classmethod
    def run(cls, args: InfoArguments, debug: bool) -> None:
        config = Config.load()
        cls.logger = Logger.load(debug=debug)
        instance = cls(args, config)
        instance.process_parameters()
        instance.process_cmd()


def _build_info_panel(media: Media, single_input: Path, locale: str = "en") -> Panel:
    """Construye el panel Rich con los metadatos del vídeo."""
    panel_width = 80
    na = locales.Metadata["not_available"]

    def _format_duration(duration: timedelta) -> str:
        """Trunca los microsegundos para mostrar solo H:MM:SS."""
        return str(timedelta(seconds=int(duration.total_seconds())))

    def _format_size(size: int) -> str:
        """Formatea bytes como GB o MB, con separador de miles según locale."""
        bt = parse_quantity(value=size, locale=locale)
        if size >= 1024**3:
            gb = parse_quantity(value=size / 1024**3, locale=locale)
            return locales.Metadata["size_gb"].format(value=gb, raw=bt)
        mb = parse_quantity(value=size / 1024**2, locale=locale)
        return locales.Metadata["size_mb"].format(value=mb, raw=bt)

    def _build_general_table() -> Table:
        table = Table(
            title=f"📁 {locales.Metadata['general']}", show_header=True, expand=True
        )
        table.add_column(locales.Metadata["field"], style="bold", ratio=1)
        table.add_column(locales.Metadata["value"], ratio=3)
        table.add_row(locales.Metadata["file"], single_input.name)
        table.add_row(locales.Metadata["container"], media.format_name or na)
        table.add_row(
            locales.Metadata["duration"],
            _format_duration(media.duration) if media.duration else na,
        )
        if media.size is not None:
            table.add_row(locales.Metadata["size"], _format_size(media.size))
        return table

    def _build_video_table(video: Video) -> Table:
        table = Table(
            title=f"🎬 {locales.Metadata['video']}", show_header=True, expand=True
        )
        table.add_column(locales.Metadata["field"], style="bold", ratio=1)
        table.add_column(locales.Metadata["value"], ratio=3)
        table.add_row(locales.Metadata["codec"], video.codec or na)
        if video.width is None or video.height is None:
            raise MissingParameterError(name="video dimension")
        table.add_row(locales.Metadata["resolution"], f"{video.width}x{video.height}")
        table.add_row(locales.Metadata["fps"], str(video.fps) if video.fps else na)
        table.add_row(
            locales.Metadata["bitrate"],
            locales.Metadata["bitrate_bps"].format(bit_rate=video.bit_rate)
            if video.bit_rate
            else na,
        )
        return table

    def _build_audio_table(audio: list[Audio]) -> Table:
        table = Table(title=f"🎵 {locales.Metadata['audio']}", expand=True)
        for column in (
            locales.Metadata["codec"],
            locales.Metadata["sample_rate"],
            locales.Metadata["channels"],
            locales.Metadata["language"],
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
        table = Table(title=f"💬 {locales.Metadata['subtitles']}", expand=True)
        for column in (
            locales.Metadata["language"],
            locales.Metadata["subtitle_title"],
            locales.Metadata["forced"],
            locales.Metadata["default"],
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
        Group(*sections),
        title=locales.Metadata["panel_title"],
        border_style="cyan",
        width=panel_width,
    )
