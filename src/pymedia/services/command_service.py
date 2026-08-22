import queue
import subprocess
import threading
from datetime import timedelta
from pathlib import Path

from rich.progress import Progress

from pymedia.errors import CommandExecutionError, OutputOnConflictError
from pymedia.logger import Logger
from pymedia.models.enums import OutputOnConflictMode

DEFAULT_STALL_TIMEOUT = 60  # segundos sin progreso antes de abortar


def resolve_output_conflict(
    output: Path,
    output_on_conflict: OutputOnConflictMode,
    logger: Logger,
) -> Path | None:
    """
    Resuelve la resolución de conflicto de salida de fichero.

    Args:
        output: Ruta de fichero de salida.
        output_on_conflict: Actuación ante un conflicto de salida.
        logger: Servicio de registro de mensajes.

    Returns:
        Ruta (Path) resuelta de fichero de salida.
    """

    def _get_available_output_path(output_path: Path) -> Path:
        """Añade sufijo incremental ante una resolución de conflicto por renombre."""
        candidate = output_path
        index = 1
        while candidate.exists():
            candidate = output_path.with_stem(f"{output_path.stem}_{index}")
            index += 1
        return candidate

    if not output.exists():
        return output

    logger.warning(key="output_exist", file_path=output)

    match output_on_conflict:
        case OutputOnConflictMode.FAIL:
            raise OutputOnConflictError()
        case OutputOnConflictMode.RENAME:
            return _get_available_output_path(output)
        case OutputOnConflictMode.REPLACE:
            return output
        case OutputOnConflictMode.SKIP:
            return None


def run_ffmpeg(
    cmd: list[str],
    description: str,
    duration: timedelta | None = None,
    stall_timeout: float = DEFAULT_STALL_TIMEOUT,
) -> None:
    """
    Ejecuta el cmd ffmpeg generado mientras registra la salida para
    mostrar una barra de progreso.

    Args:
        cmd: Comando ffmpeg a ejecutar.
        duration: duración estimada de la duración de procedimiento del comando.
        description: Mensaje a mostrar junto a la barra de progreso
                (el nombre del comando).
        stall_timeout: Tiempo de espera, en segundos, de la aplicación para matar
                el proceso si no se recibe avance.

    Raises:
        CommandExecutionError: Si falla el cmd o se bloquea.
    """

    def _read_stdout() -> None:
        """Recepción de la evolución del comando ffmpeg."""
        for line_ in proc.stdout:  # type: ignore[union-attr]
            lines.put(line_)
        lines.put(None)  # sentinel: fin de stream

    def _abort(reason: str) -> None:
        """Mata el proceso si no se ha recibido avance durante el tiempo establecido."""
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
        total_seconds = duration.total_seconds() if duration is not None else None
        task = progress.add_task(description, total=total_seconds)

        while True:
            try:
                line = lines.get(timeout=stall_timeout)
            except queue.Empty:
                _abort(f"ffmpeg atascado: sin progreso en {stall_timeout}s")
            if line is None:
                break
            if line.startswith("out_time_ms="):
                value = line.partition("=")[2].strip()
                if value.isdigit():
                    progress.update(task, completed=int(value) / 1_000_000)

        if total_seconds is not None:
            progress.update(task, completed=total_seconds)

    proc.wait()
    stderr_thread.join()

    if proc.returncode != 0:
        raise CommandExecutionError(
            command_name=description, error="".join(stderr_lines)
        )
