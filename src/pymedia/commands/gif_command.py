from pymedia.commands.base_command import BaseCommand, SingleCommand
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingParameterError,
)
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.locales import _  # noqa
from pymedia.models.enums import OverwriteMode, ScaleMode
from pymedia.models.pipeline.gif_pipeline import GifArguments, GifParameters
from pymedia.typer_options import (
    DebugOption,
    FpsGifOption,
    HelpOption,
    InputSingleArgument,
    OutputOption,
    OverwriteOption,
    ScaleModeOption,
    ScaleToOption,
    ScaleUpscaleOption,
    TimestampEndOption,
    TimestampStartOption,
)


class GifCommand(SingleCommand[GifArguments, GifParameters]):
    name = "gif"
    help = _("Generates an animated GIF from the specified video.")

    @staticmethod
    def cli(
        input_single: InputSingleArgument,
        output: OutputOption = None,
        overwrite: OverwriteOption = OverwriteMode.ASK,
        fps: FpsGifOption = 15,
        scale_to: ScaleToOption = "640x360",
        scale_mode: ScaleModeOption = ScaleMode.FIT,
        scale_upscale: ScaleUpscaleOption = False,
        timestamp_start: TimestampStartOption = None,
        timestamp_end: TimestampEndOption = None,
        debug: DebugOption = False,
        help_: HelpOption = False,
    ) -> None:
        GifCommand.run(
            args=BaseCommand.build_args(
                args_cls=GifArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self) -> None:
        self.params = GifParameters.create(args=self.args, logger=self.logger)

    def process_cmd(self) -> None:
        if self.params.input_single is None:
            raise MissingParameterError(name="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))
        cmd = gif_cmd(params=self.params)
        if cmd is None:
            raise CommandGenerationError(name=self.name)
        self.cmd = cmd

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=self.cmd)

        self.run_ffmpeg(
            cmd=self.cmd,
            media=self.params.media,
            description=_("Generating GIF"),
            stall_timeout=self.config.app.stall_timeout,
            command_name=self.name,
        )

        self.logger.info(
            _("GIF generated successfully: %(output)s"), output=self.params.output
        )
