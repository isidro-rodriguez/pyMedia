import subprocess
from pathlib import Path

from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.logger import get_logger
from pymedia.models.arguments import Arguments
from pymedia.models.errors import CommandExecutionError
from pymedia.models.state import state
from pymedia.services.commands_service import initialize_command

logger = get_logger("gif")


def gif_command(args: Arguments) -> None:
    initialize_command(args)
    path = state.inputs[0]

    if state.output:
        output = state.output.absolute()
    else:
        output = Path(path.stem + ".gif").absolute()

    cmd = gif_cmd(output)

    try:
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        logger.info(f"Generado correctamente GIF: {output}")
    except subprocess.CalledProcessError as e:
        raise CommandExecutionError("gif", e.stderr) from e
