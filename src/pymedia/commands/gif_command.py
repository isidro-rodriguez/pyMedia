from pymedia import locales
from pymedia.commands.command import Command
from pymedia.errors import CommandGenerationError
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.models.enums import OverwriteMode
from pymedia.models.gif_model import GifArguments, GifParameters
from pymedia.typer_options import (
    DebugOption,
    EndOption,
    FpsOption,
    HelpOption,
    InputSingleArgument,
    OutputOption,
    OverwriteOption,
    ScaleGifOption,
    StartOption,
)


class GifCommand(Command[GifArguments, GifParameters]):
    name = "gif"

    @staticmethod
    def cli(
        input_single: InputSingleArgument,
        output: OutputOption = None,
        overwrite: OverwriteOption = OverwriteMode.ASK,
        fps: FpsOption = 15,
        scale: ScaleGifOption = 480,
        timestamp_start: StartOption = None,
        timestamp_end: EndOption = None,
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
        self.params = GifParameters.create(args=self.args, config=self.config)

    def process_cmd(self) -> None:
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
