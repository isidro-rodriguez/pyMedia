"""Ejecución de comandos ffmpeg con progreso, temporal y confirmación atómica.

Separa las piezas puras (preparación, staging, commit, progreso) del ciclo de
vida del proceso (`FfmpegProcess`), para poder testearlas por separado.
"""

import queue
import subprocess
import tempfile
import threading
from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path
from typing import Self, TextIO

from rich.progress import Progress

from pymedia.errors import CommandError, OsError, UserError
from pymedia.locales import translate as _

STDOUT, STDERR = "stdout", "stderr"


def prepare_command(cmd: list[str], overwrite: bool) -> list[str]:
    """Añade `-nostdin` y la política de sobrescritura si el binario es ffmpeg.

    ffmpeg no debe preguntar por su cuenta: el prompt quedaría oculto tras la
    barra de progreso y bloquearía el proceso.

    Args:
        cmd: Comando ya construido.
        overwrite: `True` para usar `-y`, `False` para usar `-n`.

    Returns:
        Comando normalizado; el mismo `cmd` si el binario no es ffmpeg.
    """
    if Path(cmd[0]).stem != "ffmpeg":
        return cmd
    flags = ("-y", "-n")
    return [
        cmd[0],
        "-nostdin",
        "-y" if overwrite else "-n",
        *(a for a in cmd[1:] if a not in flags),
    ]


def stage_outputs(cmd: list[str], outputs: Iterable[str], staging: Path) -> list[str]:
    """Redirige al directorio temporal los argumentos de salida del comando.

    La salida principal (o su plantilla `%03d`) es siempre el último argumento;
    `outputs` aporta el resto en comandos multisalida.

    Args:
        cmd: Comando ffmpeg.
        outputs: Rutas de salida, como cadenas, presentes en `cmd`.
        staging: Directorio temporal de destino.

    Returns:
        Copia de `cmd` con las salidas apuntando a `staging`.
    """
    targets = {cmd[-1], *outputs}
    return [
        str(staging / Path(arg).name) if i and arg in targets else arg
        for i, arg in enumerate(cmd)
    ]


def commit_outputs(staging: Path, dest_dir: Path, overwrite: bool) -> None:
    """Mueve las salidas completas del temporal a su destino final.

    Args:
        staging: Directorio temporal con las salidas generadas.
        dest_dir: Directorio de destino.
        overwrite: Si `False`, un fichero preexistente aborta el movimiento.

    Raises:
        CommandError: Si una salida ya existe y no se puede sobrescribir.
        OsError: Si no se puede mover una salida a su destino final.
    """
    staged = sorted(staging.iterdir())
    for file in staged:
        if not overwrite and (dest_dir / file.name).exists():
            raise CommandError(
                msg=_("Output file already exists: %(name)s") % {"name": file.name}
            )
    try:
        for file in staged:
            file.replace(dest_dir / file.name)
    except OSError as e:
        raise OsError(msg=_("Output file could not be moved.")) from e


@dataclass(slots=True)
class ProgressTracker:
    """Traduce las líneas de ffmpeg a progreso absoluto.

    Attributes:
        progress_time: Duración a procesar; activa el progreso por tiempo.
        total_steps: Pasos `showinfo` esperados; activa el progreso por pasos.
            Si se dan ambos, prevalece el tiempo.
    """

    progress_time: timedelta | None = None
    total_steps: int | None = None
    _steps: int = 0

    @property
    def total(self) -> float | None:
        """Total de la barra, o `None` si el progreso es indeterminado."""
        if self.progress_time is not None:
            return self.progress_time.total_seconds()
        return None if self.total_steps is None else float(self.total_steps)

    def update(self, source: str, line: str) -> float | None:
        """Procesa una línea de salida de ffmpeg.

        Args:
            source: Origen de la línea (`STDOUT` o `STDERR`).
            line: Línea recibida.

        Returns:
            Progreso absoluto actualizado, o `None` si la línea no lo modifica.
        """
        if self.progress_time is not None and line.startswith("out_time_ms="):
            value = line.partition("=")[2].strip()
            return int(value) / 1_000_000 if value.isdigit() else None
        if self.total_steps is not None and source == STDERR:
            self._steps += 1
            return float(self._steps)
        return None


class FfmpegProcess:
    """Proceso ffmpeg con lectores de stdout/stderr; se limpia solo al salir.

    Uso como gestor de contexto: al salir, incluso con excepción, mata el
    proceso si sigue vivo, espera a los hilos y cierra los pipes.

    Attributes:
        stderr_lines: Todas las líneas recibidas por stderr.
    """

    def __init__(self, cmd: list[str], *, capture_steps: bool) -> None:
        """Prepara el proceso sin lanzarlo.

        Args:
            cmd: Comando a ejecutar.
            capture_steps: Si `True`, emite como evento las líneas `showinfo`
                de stderr para el progreso por pasos.
        """
        self._cmd = cmd
        self._capture_steps = capture_steps
        self._events: queue.Queue[tuple[str, str | None]] = queue.Queue()
        self._threads: list[threading.Thread] = []
        self._proc: subprocess.Popen[str] | None = None
        self.stderr_lines: list[str] = []

    def __enter__(self) -> Self:
        """Lanza el proceso y arranca los hilos lectores."""
        self._proc = proc = subprocess.Popen(
            args=self._cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.DEVNULL,
            text=True,
            errors="replace",
            bufsize=1,
        )
        for name, stream in ((STDOUT, proc.stdout), (STDERR, proc.stderr)):
            thread = threading.Thread(
                target=self._pump, args=(name, stream), daemon=True
            )
            thread.start()
            self._threads.append(thread)
        return self

    def __exit__(self, *_exc: object) -> None:
        """Mata el proceso si sigue vivo y libera hilos y pipes."""
        proc = self._proc
        if proc is None:
            return
        if proc.poll() is None:
            proc.kill()
        proc.wait()
        for thread in self._threads:
            thread.join()
        for stream in (proc.stdout, proc.stderr):
            if stream is not None:
                stream.close()

    def _pump(self, name: str, stream: TextIO) -> None:
        """Lee un stream línea a línea y publica eventos en la cola.

        Args:
            name: Nombre del stream (`STDOUT` o `STDERR`).
            stream: Stream de texto a consumir.
        """
        for line in stream:
            if name == STDERR:
                self.stderr_lines.append(line)
                if not (self._capture_steps and "pts_time:" in line):
                    continue
            self._events.put((name, line))
        self._events.put((name, None))  # sentinel: fin de stream

    def events(self, stall_timeout: float) -> Iterator[tuple[str, str]]:
        """Emite `(origen, línea)` hasta que ambos streams terminan.

        Args:
            stall_timeout: Segundos máximos de espera entre eventos.

        Yields:
            Tuplas `(origen, línea)`.

        Raises:
            queue.Empty: Si no llega ningún evento en `stall_timeout`.
        """
        pending = {STDOUT, STDERR}
        while pending:
            source, line = self._events.get(timeout=stall_timeout)
            if line is None:
                pending.discard(source)
            else:
                yield source, line

    def wait(self) -> int:
        """Espera a que termine el proceso.

        Returns:
            Código de salida.
        """
        assert self._proc is not None
        return self._proc.wait()

    @property
    def stderr_tail(self) -> str:
        """Últimas 10 líneas de stderr, para informar de fallos."""
        return "".join(self.stderr_lines[-10:]).strip()


def run_ffmpeg(
    cmd: list[str],
    *,
    description: str,
    outputs: Iterable[Path],
    overwrite: bool,
    stall_timeout: float,
    command_name: str,
    progress_time: timedelta | None = None,
    total_steps: int | None = None,
) -> None:
    """Ejecuta ffmpeg mostrando una barra de progreso.

    ffmpeg escribe en un directorio temporal contiguo al destino y las salidas
    solo se mueven a su ruta final si el proceso termina bien, por lo que un
    fallo o una interrupción nunca tocan ficheros preexistentes.

    Args:
        cmd: Comando ffmpeg ya construido.
        description: Mensaje junto a la barra de progreso.
        outputs: Ficheros de salida presentes en `cmd`; se consume una vez.
        overwrite: Si se permite sobrescribir ficheros existentes.
        stall_timeout: Segundos sin actividad antes de dar el proceso por bloqueado.
        command_name: Nombre del comando, para los mensajes de error.
        progress_time: Duración del tramo a procesar (progreso por tiempo).
        total_steps: Pasos `showinfo` esperados (progreso por pasos).

    Raises:
        CommandError: Si ffmpeg falla, se bloquea o una salida ya existe.
        UserError: Si el usuario interrumpe la ejecución.
        OsError: Si no se puede mover una salida a su destino final.
    """
    dest_dir = Path(cmd[-1]).parent
    tracker = ProgressTracker(progress_time, total_steps)
    with tempfile.TemporaryDirectory(
        dir=dest_dir, prefix=".pymedia-", ignore_cleanup_errors=True
    ) as tmp:
        staging = Path(tmp)
        staged_cmd = stage_outputs(
            cmd=prepare_command(cmd=cmd, overwrite=overwrite),
            outputs=(str(o) for o in outputs),
            staging=staging,
        )
        try:
            with (
                FfmpegProcess(
                    cmd=staged_cmd,
                    capture_steps=total_steps is not None,
                ) as proc,
                Progress() as progress,
            ):
                task = progress.add_task(description=description, total=tracker.total)
                for source, line in proc.events(stall_timeout):
                    if (done := tracker.update(source=source, line=line)) is not None:
                        progress.update(task_id=task, completed=done)
                returncode = proc.wait()
                if returncode == 0 and tracker.total is not None:
                    progress.update(task_id=task, completed=tracker.total)
        except KeyboardInterrupt:
            raise UserError(
                msg=_("FFmpeg command interrupted manually: %(command_name)s")
                % {"command_name": command_name}
            ) from None
        except queue.Empty:
            raise CommandError(
                msg=_("FFmpeg command timed out: %(command_name)s")
                % {"command_name": command_name}
            ) from None

        if returncode != 0:
            tail = proc.stderr_tail
            detail = f"\nffmpeg stderr:\n{tail}" if tail else ""
            raise CommandError(
                msg=_("FFmpeg command failed during execution.") + detail
            )

        commit_outputs(staging=staging, dest_dir=dest_dir, overwrite=overwrite)
