import subprocess
from pathlib import Path

from pymedia.feedback.errors import (
    CommandExecutionError,
    CommandGenerationError,
)
from pymedia.feedback.logger import get_logger, log_debug, log_info
from pymedia.ffmpeg.encode_cmd import encode_cmd
from pymedia.models.arguments import Arguments
from pymedia.models.state import state
from pymedia.services.commands_service import (
    initialize_command,
    resolve_output_conflict,
)

logger = get_logger("encode")


def encode_command(args: Arguments, output: Path | None = None) -> None:
    if not output:  # normal encode
        initialize_command(args)
    else:  # split auxiliar operation
        state.output = output
        state.set_video_pipeline()

    for i in range(len(state.media)):
        if state.output and len(state.media) == 1:
            output = state.output.absolute()
        elif state.output and len(state.media) > 1:
            p = state.output
            output = Path(f"{p.parent}/{p.stem}_{i}{p.suffix}").absolute()
        else:
            output = Path(
                f"{state.inputs[i].stem}_encoded{state.config.encode.default_container}"
            ).absolute()

        output = resolve_output_conflict(output, logger)

        if output is None:
            return

        cmd = encode_cmd(state.inputs[i], output)

        if cmd is None:
            raise CommandGenerationError(command_name="encode")

        log_debug(logger, "ffmpeg_command", cmd=cmd)
        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            log_info(logger, "encode_success", output=output)
        except subprocess.CalledProcessError as e:
            raise CommandExecutionError(command_name="encode", error=e.stderr) from e
