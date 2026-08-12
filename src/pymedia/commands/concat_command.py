import subprocess
import tempfile
from pathlib import Path

from pymedia.feedback.errors import (
    CommandExecutionError,
    CommandGenerationError,
    FFmpegTimeoutError,
    IncompatibleFilesError,
)
from pymedia.feedback.logger import get_logger, log_debug, log_info
from pymedia.ffmpeg.concat_demux_cmd import concat_demux_cmd
from pymedia.ffmpeg.concat_filter_cmd import concat_filter_cmd
from pymedia.models.arguments import Arguments
from pymedia.models.state import state
from pymedia.services.commands_service import (
    initialize_command,
    resolve_output_conflict,
)

logger = get_logger("concat")

# Timeout en segundos para la ejecución de ffmpeg (30 minutos)
FFMPEG_TIMEOUT = 1800


def _compatible_videos() -> bool:
    reference = state.media[0].concat_signature
    return all(m.concat_signature == reference for m in state.media[1:])


def _run_ffmpeg(cmd: list[str]) -> None:
    """Ejecuta ffmpeg con timeout y manejo de errores."""
    log_debug(logger, "ffmpeg_command", cmd=cmd)
    try:
        subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=FFMPEG_TIMEOUT,
        )
        log_info(logger, "concat_success", output=state.output)
    except subprocess.TimeoutExpired as exc:
        raise FFmpegTimeoutError() from exc
    except subprocess.CalledProcessError as e:
        raise CommandExecutionError(command_name="concat", error=e.stderr) from e


def concat_command(args: Arguments):
    initialize_command(args)

    if not state.output:
        state.output = Path(state.inputs[0].stem + "_concat" + state.inputs[0].suffix)

    state.output = resolve_output_conflict(state.output, logger)

    if state.output is None:
        return

    media = state.media

    # Verificar que no se mezclen vídeos con y sin audio
    has_audio = [m.audio is not None for m in media]
    if any(has_audio) and not all(has_audio):
        raise IncompatibleFilesError()

    # Si son compatibles y no se realiza transcodificación, se usa concat demux
    if _compatible_videos() and state.video_pipeline.requires_encode is False:
        with tempfile.TemporaryDirectory() as tmp_dir:
            list_txt = Path(tmp_dir) / "list.txt"
            with open(list_txt, "w", encoding="utf-8") as f:
                for p in state.inputs:
                    f.write(f"file '{p.resolve().as_posix()}'\n")

            cmd = concat_demux_cmd(list_txt)

            if cmd is None:
                raise CommandGenerationError(command_name="concat")

            _run_ffmpeg(cmd)

    # Si no son compatibles o hay operaciones, se usa concat filter (recodificación)
    else:
        cmd = concat_filter_cmd()
        _run_ffmpeg(cmd)
