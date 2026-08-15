from pathlib import Path

from pymedia import locales
from pymedia.errors import CommandGenerationError
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.logger import get_logger, log_debug, log_info
from pymedia.models.arguments import Arguments
from pymedia.models.state import state
from pymedia.services.command_service import (
    initialize_command,
    resolve_output_conflict,
    run_ffmpeg,
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

    if cmd is None:
        raise CommandGenerationError(command_name="gif")

    log_debug(logger, "ffmpeg_command", cmd=cmd)
    run_ffmpeg(
        cmd=cmd,
        duration=state.media[0].duration.total_seconds(),
        description=locales.Progress["gif"],
    )
    log_info(logger, "gif_success", output=output)
