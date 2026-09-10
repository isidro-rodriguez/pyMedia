"""Clases base de los subcomandos de la CLI de pyMedia.

Define el ciclo de vida común (carga de configuración, parseo de parámetros,
resolución de sobrescritura, construcción y ejecución de ffmpeg) para comandos
de fichero único y de procesamiento por lotes.
"""

import queue
import subprocess
import threading
from abc import ABC
from datetime import timedelta
from pathlib import Path
from typing import TypeVar

import typer
from rich.progress import Progress

from pymedia.errors import (
    CommandError,
    InvalidParameterError,
)
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.types import OverwriteMode

ParamsT = TypeVar("ParamsT")


class BasePipeline[ParamsT](ABC):
    """Clase abstracta que define la base de los comandos del programa.

    Attributes:
        command_name: Nombre del comando.
        config: Parámetros que determinan el funcionamiento de la aplicación.
        logger: Interfaz principal de la aplicación para generar mensajes.
        params: Parámetros parseados y validados a partir de `args`.
    """

    params: ParamsT

    def __init__(self, debug: bool) -> None:
        """Inicializa el comando con argumentos de tipo definido y la config cargada.

        Args:
            debug: Habilita el nivel de log DEBUG.
        """
        command_name = self.__class__.__name__
        if not command_name.endswith("Pipeline"):
            raise InvalidParameterError(msg=_("Invalid class name format!"))
        self.command_name = command_name.removesuffix("Pipeline")
        self.config = Config.load()
        self.logger = Logger.create(debug=debug)

    def resolve_overwrite(self, output_list: list[Path]) -> bool:
        """Comprueba si algún fichero de salida existe y resuelve la sobrescritura."""

        def conflict_ask(file: Path) -> bool:
            self.logger.warning(_(f"Output file already exists: {file.name}"))
            if typer.confirm(_("Overwrite?")):
                self.params.overwrite = OverwriteMode.YES
                return True
            self.logger.warning(_("Process skipped since output file already exists."))
            return False

        if self.params.overwrite == OverwriteMode.ASK:
            return True

        for output in output_list:
            if output.exists():
                if not conflict_ask(file=output):
                    return False
        return True

    def run_ffmpeg(
        self,
        cmd: list[str],
        description: str,
        progress_time: timedelta | None = None,
        total_steps: int | None = None,
    ) -> None:
        """Ejecuta el cmd ffmpeg generado mientras muestra una barra de progreso.

        El progreso se reporta de tres formas posibles, según los parámetros
        recibidos: por tiempo (`progress_time`, vía `out_time_ms` en stdout),
        por pasos (`total_steps`, contando eventos `showinfo` en stderr) o de
        forma indeterminada (barra pulsante) si no se aporta ninguno.

        Args:
            cmd: Comando ffmpeg ya construido, listo para ejecutar.
            description: Mensaje a mostrar junto a la barra de progreso.
            progress_time: Duración del tramo de vídeo a procesar.
            total_steps: Número de pasos esperados de `showinfo` por stderr.

        Raises:
            CommandError: Si falla el cmd o se bloquea.
        """

        def _read_stdout() -> None:
            """Recepción de la evolución del comando ffmpeg vía -progress."""
            for line_ in proc.stdout:  # type: ignore[union-attr]
                events.put(("stdout", line_))
            events.put(("stdout", None))  # sentinel: fin de stream

        def _read_stderr() -> None:
            """Almacena stderr y emite eventos showinfo para el progreso por pasos."""
            for line_ in proc.stderr:  # type: ignore[union-attr]
                stderr_lines.append(line_)
                if total_steps is not None and "pts_time:" in line_:
                    events.put(("stderr", line_))
            events.put(("stderr", None))  # sentinel: fin de stream

        def _abort() -> None:
            """Mata el proceso si no se ha recibido avance en el tiempo establecido."""
            proc.kill()
            proc.wait()
            stderr_thread.join()
            stdout_thread.join()
            raise CommandError(
                msg=_("FFmpeg command timed out: %(command_name)s")
                % {"command_name": self.command_name}
            )

        proc = subprocess.Popen(
            args=cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

        assert proc.stdout is not None
        assert proc.stderr is not None
        stderr_lines: list[str] = []
        events: queue.Queue[tuple[str, str | None]] = queue.Queue()

        stdout_thread = threading.Thread(target=_read_stdout, daemon=True)
        stderr_thread = threading.Thread(target=_read_stderr, daemon=True)
        stdout_thread.start()
        stderr_thread.start()

        with Progress() as progress:
            if progress_time is not None:
                total: float | None = progress_time.total_seconds()
            elif total_steps is not None:
                total = float(total_steps)
            else:
                total = None
            task = progress.add_task(description=description, total=total)

            pending_streams = {"stdout", "stderr"}
            completed_steps = 0
            while pending_streams:
                try:
                    source, line = events.get(timeout=self.config.app.stall_timeout)
                except queue.Empty:
                    _abort()

                if line is None:
                    pending_streams.discard(source)
                    continue

                if progress_time is not None and line.startswith("out_time_ms="):
                    value = line.partition("=")[2].strip()
                    if value.isdigit():
                        progress.update(task_id=task, completed=int(value) / 1_000_000)
                elif total_steps is not None and source == "stderr":
                    completed_steps += 1
                    progress.update(task_id=task, completed=completed_steps)

            if total is not None:
                progress.update(task_id=task, completed=total)

        proc.wait()
        stderr_thread.join()
        stdout_thread.join()

        if proc.returncode != 0:
            tail = "".join(stderr_lines[-10:]).strip()
            detail = f"\nffmpeg stderr:\n{tail}" if tail else ""
            raise CommandError(
                msg=_("FFmpeg command failed during execution.") + detail
            )
