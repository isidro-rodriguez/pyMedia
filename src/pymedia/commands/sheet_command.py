import tempfile
from pathlib import Path

from pymedia.commands.base_command import BaseCommand, BatchCommand
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingParameterError,
)
from pymedia.ffmpeg.sheet_cmd import sheet_cmd
from pymedia.locales import _
from pymedia.models.enums import OverwriteMode, PresetsSheetMode
from pymedia.models.pipeline.sheet_pipeline import SheetArguments, SheetParameters
from pymedia.typer_options import (
    DebugOption,
    HelpOption,
    InputListArgument,
    OutputDirectoryOption,
    OutputOption,
    OverwriteOption,
    PresetSheetOption,
)


class SheetCommand(BatchCommand[SheetArguments, SheetParameters]):
    name = "sheet"
    help = _("Generates a thumbnail grid sheet with media info header.")

    @staticmethod
    def cli(
        input_list: InputListArgument,
        output: OutputOption = None,
        output_directory: OutputDirectoryOption = None,
        overwrite: OverwriteOption = OverwriteMode.ASK,
        preset_sheet: PresetSheetOption = PresetsSheetMode.HD,
        debug: DebugOption = False,
        help_: HelpOption = False,
    ) -> None:
        SheetCommand.run(
            args=BaseCommand.build_args(
                args_cls=SheetArguments,
                local_vars=locals(),
            ),
            debug=debug,
        )

    def process_parameters(self, input_single: Path) -> SheetParameters:
        return SheetParameters.create(
            args=self.args, logger=self.logger, input_single=input_single
        )

    def process_cmd(self, params: SheetParameters) -> None:
        if params.input_single is None:
            raise MissingParameterError(name="input_single")
        if params.media is None:
            raise MissingMediaError(path=str(params.input_single))

        with tempfile.TemporaryDirectory() as tmp_dir:
            tile_tmp = Path(tmp_dir) / "tile_tmp.jpg"

            snapshots_cmd, header_cmd = sheet_cmd(params=params, tile_tmp=tile_tmp)

            if snapshots_cmd is None:
                raise CommandGenerationError(command_name="generate_sheet_cmd")
            self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=snapshots_cmd)

            if header_cmd is None:
                raise CommandGenerationError(command_name="generate_header_cmd")
            self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=header_cmd)

            self.run_ffmpeg(
                cmd=snapshots_cmd,
                media=params.media,
                description=_("Generating sheet snapshots"),
                stall_timeout=self.config.app.stall_timeout,
                command_name=self.name,
            )

            self.run_ffmpeg(
                cmd=header_cmd,
                media=params.media,
                description=_("Generating sheet header"),
                stall_timeout=self.config.app.stall_timeout,
                command_name=self.name,
            )

        self.logger.info(
            _("Metadata generated successfully: %(output)s"), output=params.output
        )
