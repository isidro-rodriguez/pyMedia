import subprocess
from pathlib import Path

from pymedia.feedback.errors import CommandExecutionError
from pymedia.feedback.logger import get_logger, log_debug, log_info
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.models.arguments import Arguments
from pymedia.models.state import state
from pymedia.services.commands_service import (
    initialize_command,
    resolve_output_conflict,
)

logger = get_logger("gif")


def gif_command(args: Arguments) -> None:
    initialize_command(args)
    path = state.inputs[0]

    if state.output:
        output = state.output.absolute()
    else:
        output = Path(path.stem + ".gif").absolute()

    output = resolve_output_conflict(output, logger)

    if output is None:
        return

    cmd = gif_cmd(output)

    log_debug(logger, "ffmpeg_command", cmd=cmd)
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        log_info(logger, "gif_success", output=output)
    except subprocess.CalledProcessError as e:
        raise CommandExecutionError(command_name="gif", error=e.stderr) from e
