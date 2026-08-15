import queue
import subprocess
import threading
from pathlib import Path

from rich.progress import Progress

from pymedia.cli_params import OutputOnConflictMode
from pymedia.errors import CommandExecutionError, OutputOnConflictError
from pymedia.logger import log_warning, setup_logging
from pymedia.models.arguments import Arguments, CommandName
from pymedia.models.state import state

DEFAULT_STALL_TIMEOUT = 60  # segundos sin progreso antes de abortar


def initialize_command(args: Arguments) -> None:
    setup_logging(debug=args.debug)
    state.set_arguments(args)
    state.set_inputs(args.inputs)
    state.set_media(args.inputs)
    if args.command is CommandName.GIF:
        state.set_gif_pipeline()
    else:
        state.set_video_pipeline()
    if args.output is not None:
        state.set_output(args.output)
    state.set_output_on_conflict()


def resolve_output_conflict(output: Path, logger) -> Path | None:
    def _get_available_output_path(output_path: Path) -> Path:
        candidate = output_path
        index = 1

        while candidate.exists():
            candidate = output_path.with_stem(f"{output_path.stem}_{index}")
            index += 1

        return candidate

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


def run_ffmpeg(
    cmd: list[str],
    duration: float,
    description: str,
    stall_timeout: float = DEFAULT_STALL_TIMEOUT,
) -> None:
    """
    Ejecuta ffmpeg mostrando progreso.
    `cmd` debe incluir ya -progress pipe:1 -nostats.
    """

    def _read_stdout() -> None:
        for line_ in proc.stdout:  # type: ignore[union-attr]
            lines.put(line_)
        lines.put(None)  # sentinel: fin de stream

    def _abort(reason: str) -> None:
        proc.kill()
        proc.wait()
        stderr_thread.join()
        stdout_thread.join()
        raise CommandExecutionError(command_name=description, error=reason)

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

    # Cola + hilo lector: permite aplicar timeout de "sin progreso"
    # sin bloquear indefinidamente en el for de stdout.
    lines: queue.Queue[str | None] = queue.Queue()

    stdout_thread = threading.Thread(target=_read_stdout, daemon=True)
    stdout_thread.start()

    with Progress() as progress:
        task = progress.add_task(description, total=duration)
        while True:
            try:
                line = lines.get(timeout=stall_timeout)
            except queue.Empty:
                _abort(f"ffmpeg atascado: sin progreso en {stall_timeout}s")
            if line is None:
                break
            if line.startswith("out_time_ms="):
                progress.update(task, completed=int(line.split("=")[1]) / 1_000_000)
        progress.update(task, completed=duration)

    proc.wait()
    stderr_thread.join()

    if proc.returncode != 0:
        raise CommandExecutionError(
            command_name=description, error="".join(stderr_lines)
        )
