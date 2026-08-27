from pathlib import Path

from pymedia import locales
from pymedia.commands.command import Command
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingParameterError,
)
from pymedia.ffmpeg.sheet_cmd import sheet_cmd
from pymedia.models.enums import OverwriteMode, PresetsSheetMode
from pymedia.models.pipeline.sheet_pipeline import SheetArguments, SheetParameters
from pymedia.typer_options import (
    DebugOption,
    HelpOption,
    InputListArgument,
    OutputOption,
    OverwriteOption,
    PresetSheetOption,
)


class SheetCommand(Command[SheetArguments, SheetParameters]):
    name = "sheet"

    @staticmethod
    def cli(
        input_list: InputListArgument,
        output: OutputOption = None,
        overwrite: OverwriteOption = OverwriteMode.ASK,
        preset: PresetSheetOption = PresetsSheetMode.HD,
        debug: DebugOption = False,
        help_: HelpOption = False,
    ) -> None:
        SheetCommand.run(
            args=Command.build_args(
                args_cls=SheetArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self, args: SheetArguments, input_single: Path) -> None:
        self.params = SheetParameters.create(
            args=args, input_single=input_single, logger=self.logger
        )

    def process_cmd(self) -> None:
        if self.params.input_single is None:
            raise MissingParameterError(name="input_single")
        if self.params.media is None:
            raise MissingMediaError(path=str(self.params.input_single))

        snapshots_cmd, header_cmd = sheet_cmd(params=self.params)

        if snapshots_cmd is None:
            raise CommandGenerationError(command_name="generate_sheet_cmd")
        self.logger.debug(key="ffmpeg_command", cmd=snapshots_cmd)

        if header_cmd is None:
            raise CommandGenerationError(command_name="generate_header_cmd")
        self.logger.debug(key="ffmpeg_command", cmd=header_cmd)

        self.run_ffmpeg(
            cmd=snapshots_cmd,
            media=self.params.media,
            description=locales.Progress["sheet_snapshots"],
            stall_timeout=self.config.app.stall_timeout,
        )

        self.run_ffmpeg(
            cmd=header_cmd,
            media=self.params.media,
            description=locales.Progress["sheet_header"],
            stall_timeout=self.config.app.stall_timeout,
        )

        self.logger.info(key="sheet_success", output=self.params.output)
