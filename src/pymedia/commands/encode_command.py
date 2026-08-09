import subprocess
from pathlib import Path

from pymedia.ffmpeg.encode_cmd import encode_cmd
from pymedia.logger import get_logger
from pymedia.models.arguments import Arguments
from pymedia.models.errors import CommandExecutionError, CommandGenerationError
from pymedia.models.state import state
from pymedia.services.commands_service import initialize_command

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

        cmd = encode_cmd(state.inputs[i], output)

        if cmd is None:
            raise CommandGenerationError("encode")

        try:
            subprocess.run(cmd, capture_output=True, text=True, check=True)
            logger.info(f"Transcodificación correcta: {output}")
        except subprocess.CalledProcessError as e:
            raise CommandExecutionError("encode", e.stderr) from e
