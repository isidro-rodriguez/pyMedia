import subprocess
import tempfile
from pathlib import Path

from pymedia.commands.encode_command import encode_command
from pymedia.errors import CommandExecutionError, CommandGenerationError
from pymedia.ffmpeg.split_cmd import split_cmd
from pymedia.logger import get_logger, log_debug, log_info
from pymedia.models.arguments import Arguments
from pymedia.models.state import state
from pymedia.services.commands_service import (
    initialize_command,
    resolve_output_conflict,
)

logger = get_logger("split")


def _split(input_single: Path, output: Path) -> None:
    """Divide un vídeo en los puntos de corte indicados."""
    cmd = split_cmd(input_single, output)

    if cmd is None:
        raise CommandGenerationError(command_name="split")

    log_debug(logger, "ffmpeg_command", cmd=cmd)
    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        log_info(logger, "split_success", output=output)
    except subprocess.CalledProcessError as e:
        raise CommandExecutionError(command_name="split", error=e.stderr) from e


def split_command(args: Arguments) -> None:
    initialize_command(args)
    pipeline = state.video_pipeline
    if state.output:
        output = state.output
    else:
        output = Path(state.inputs[0].name)

    output = resolve_output_conflict(output, logger)

    if output is None:
        return

    if pipeline.requires_encode:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir) / (
                state.inputs[0].stem + "_tmp" + state.inputs[0].suffix
            )
            encode_command(args, tmp_path)
            _split(tmp_path, output)
    else:
        _split(state.inputs[0], output)
