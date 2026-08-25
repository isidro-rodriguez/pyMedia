from pymedia import locales
from pymedia.commands.command import Command
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingParameterError,
)
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.models.enums import OverwriteMode
from pymedia.models.pipeline.gif_pipeline import GifArguments, GifParameters
from pymedia.typer_options import (
    DebugOption,
    FpsGifOption,
    HelpOption,
    InputSingleArgument,
    OutputOption,
    OverwriteOption,
    ResizeHeightOption,
    ResizeUpscaleOption,
    ResizeWidthOption,
    TimestampEndOption,
    TimestampStartOption,
)


class GifCommand(Command[GifArguments, GifParameters]):
    name = "gif"

    @staticmethod
    def cli(
        input_single: InputSingleArgument,
        output: OutputOption = None,
        overwrite: OverwriteOption = OverwriteMode.ASK,
        fps: FpsGifOption = 15,
        resize_width: ResizeWidthOption = None,
        resize_height: ResizeHeightOption = None,
        resize_upscale: ResizeUpscaleOption = False,
        timestamp_start: TimestampStartOption = None,
        timestamp_end: TimestampEndOption = None,
        debug: DebugOption = False,
        help_: HelpOption = False,
    ) -> None:
        GifCommand.run(
            args=Command.build_args(
                args_cls=GifArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self) -> None:
        self.params = GifParameters.create(args=self.args, logger=self.logger)

    def process_cmd(self) -> None:
        if self.params.input_single is None:
            raise MissingParameterError(parameter="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))
        cmd = gif_cmd(params=self.params)
        if cmd is None:
            raise CommandGenerationError(command_name=self.name)
        self.cmd = cmd

        self.logger.debug(key="ffmpeg_command", cmd=self.cmd)

        self.run_ffmpeg(
            cmd=self.cmd,
            media=self.params.media,
            description=locales.Progress[self.name],
            stall_timeout=self.config.app.stall_timeout,
        )

        self.logger.info(key="gif_success", output=self.params.output)
