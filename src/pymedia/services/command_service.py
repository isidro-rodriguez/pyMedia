import subprocess
import threading
from pathlib import Path

from rich.progress import Progress

from pymedia.cli_params import OutputOnConflictMode
from pymedia.errors import CommandExecutionError, OutputOnConflictError
from pymedia.logger import log_warning, setup_logging
from pymedia.models.arguments import Arguments, CommandName
from pymedia.models.state import state


def initialize_command(args: Arguments) -> None:
    setup_logging(debug=args.debug)
    state.set_arguments(args)
    state.set_inputs(args.inputs)
    state.set_media(args.inputs)
    if args.output is not None:
        state.set_output(args.output)
    if args.command is CommandName.GIF:
        state.set_gif_pipeline()
    else:
        state.set_video_pipeline()
    state.set_output_on_conflict()


def _get_available_output_path(output: Path) -> Path:
    candidate = output
    index = 1

    while candidate.exists():
        candidate = output.with_stem(f"{output.stem}_{index}")
        index += 1

    return candidate


def resolve_output_conflict(output: Path, logger) -> Path | None:
    if not output.exists():
        return output

    log_warning(logger, "output_exist", file_path=output)

    match state.output_on_conflict:
        case OutputOnConflictMode.FAIL:
            raise OutputOnConflictError()

        case OutputOnConflictMode.RENAME:
            return _get_available_output_path(output)

        case OutputOnConflictMode.REPLACE:
            return output

        case OutputOnConflictMode.SKIP:
            return None

    return None


def run_ffmpeg(cmd: list[str], duration: float, description: str) -> None:
    """
    Ejecuta ffmpeg mostrando progreso.
    `cmd` debe incluir ya -progress pipe:1 -nostats.
    """
    proc = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1
    )

    assert proc.stdout is not None
    assert proc.stderr is not None
    stderr = proc.stderr

    # Drenar stderr en un hilo aparte: si nadie lo lee, su buffer se
    # llena y ffmpeg se bloquea -> deadlock con el bucle de stdout.
    stderr_lines: list[str] = []
    stderr_thread = threading.Thread(
        target=lambda: stderr_lines.extend(stderr), daemon=True
    )
    stderr_thread.start()

    with Progress() as progress:
        task = progress.add_task(description, total=duration)
        for line in proc.stdout:
            if line.startswith("out_time_ms="):
                progress.update(task, completed=int(line.split("=")[1]) / 1_000_000)
        progress.update(task, completed=duration)  # remata al 100%

    # Asegura que ya ha acabado antes de mirar el returncode.
    proc.wait()
    stderr_thread.join()

    if proc.returncode != 0:
        raise CommandExecutionError(
            command_name=description, error="".join(stderr_lines)
        )
