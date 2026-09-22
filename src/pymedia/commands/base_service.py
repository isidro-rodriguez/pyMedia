"""Clases base de los servicios de pyMedia.

Define los servicios comunes para los comandos.
"""

import os
import queue
import re
import shlex
import subprocess
import sys
import tempfile
import threading
from abc import ABC
from collections.abc import Iterable
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Never, Protocol, TypeVar, cast

import typer
from rich.progress import Progress

from pymedia.errors import (
    CommandError,
    InvalidParameterError,
    OsError,
    UserError,
)
from pymedia.locales import _
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.types import OverwriteMode


class _OverwriteParams(Protocol):
    """Parámetros capaces de resolver la sobrescritura de ficheros de salida."""

    overwrite: OverwriteMode


class _AbortMode(Enum):
    """Escenarios en los que se puede interrumpir el comando Ffmpeg."""

    FFMPEG = "ffmpeg"
    MANUAL = "manual"
    TIMEOUT = "timeout"


_UNSAFE_CHARS = re.compile(r"[^\w@%+=:,./-]")


ParamsT = TypeVar("ParamsT")


class BaseService[ParamsT](ABC):
    """Clase abstracta que define la base de los comandos del programa.

    Attributes:
        command_name: Nombre del comando.
        config: Parámetros que determinan el funcionamiento de la aplicación.
        logger: Interfaz principal de la aplicación para generar mensajes.
        params: Parámetros parseados y validados a partir de `args`.
    """

    params: ParamsT

    def __init__(
        self, params: ParamsT, debug: bool = False, show_cmd: bool = False
    ) -> None:
        """Inicializa el comando con argumentos de tipo definido y la config cargada.

        Args:
            debug: Habilita el nivel de log DEBUG.
            show_cmd: Si `True`, muestra el comando ffmpeg compuesto al usuario.
            params: Parámetros del comando.

        Raises:
            InvalidParameterError: Si el nombre de la clase no termina en `Service`.
        """
        command_name = self.__class__.__name__
        if not command_name.endswith("Service"):
            raise InvalidParameterError(msg=_("Invalid class name format!"))
        self.command_name = command_name.removesuffix("Service")
        self.config = Config.load()
        self.debug = debug
        self.show_cmd = show_cmd
        self.logger = Logger.load()
        self.params = params

    def resolve_overwrite(self, output_list: list[Path]) -> bool:
        """Comprueba si algún fichero de salida existe y resuelve la sobrescritura.

        Args:
            output_list: Lista de ficheros de salida a comprobar.

        Returns:
            `True` si se puede sobrescribir o no hay conflicto, `False` si el
            proceso debe omitirse.
        """
        params = cast(_OverwriteParams, self.params)
        if params.overwrite == OverwriteMode.YES:
            return True

        process_skip_msg = _("Process skipped since output file already exists.")
        for output in output_list:
            if output.exists():
                if params.overwrite == OverwriteMode.NO:
                    self.logger.warning(process_skip_msg)
                    return False
                self.logger.warning(
                    _("Output file already exists: %(name)s") % {"name": output.name}
                )
                if typer.confirm(_("Overwrite?")):
                    params.overwrite = OverwriteMode.YES
                    return True
                self.logger.warning(process_skip_msg)
                return False
        return True

    def display_cmd(self, cmd: list[str]) -> None:
        """Muestra el comando compuesto al usuario si ha activado debug o show-cmd."""

        def _quote_windows(token: str) -> str:
            """Entrecomilla un token si contiene caracteres especiales."""
            if not _UNSAFE_CHARS.search(token):
                return token
            return '"' + token.replace('"', '\\"') + '"'

        def _format_cmd(cmd: list[str]) -> str:
            """Format a command list as a copy-pasteable shell string."""
            if os.name == "nt":
                return " ".join(_quote_windows(t) for t in cmd)
            return shlex.join(cmd)

        if self.show_cmd:
            self.logger.print(
                renderable=f"\n{_format_cmd(cmd=cmd)}\n",
                emoji=False,
                soft_wrap=True,
            )
            sys.exit(0)

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        if self.debug and not typer.confirm(
            text=_("Do you want to run this ffmpeg command?")
        ):
            self.logger.warning(msg=_("User decided to abort process."))
            sys.exit(0)

    def run_ffmpeg(
        self,
        cmd: list[str],
        description: str,
        output_list: Iterable[Path],
        progress_time: timedelta | None = None,
        total_steps: int | None = None,
    ) -> None:
        """Ejecuta el cmd ffmpeg generado mientras muestra una barra de progreso.

        ffmpeg escribe en un directorio temporal contiguo al destino y las
        salidas solo se mueven a su ruta final si el proceso termina bien, por
        lo que un fallo o una interrupción nunca tocan ficheros preexistentes.

        El progreso se reporta de tres formas posibles, según los parámetros
        recibidos: por tiempo (`progress_time`, vía `out_time_ms` en stdout),
        por pasos (`total_steps`, contando eventos `showinfo` en stderr) o de
        forma indeterminada (barra pulsante) si no se aporta ninguno.

        Args:
            cmd: Comando ffmpeg ya construido, listo para ejecutar.
            description: Mensaje a mostrar junto a la barra de progreso.
            output_list: Ficheros de salida que recibe `cmd` como argumento;
                se consume una sola vez. La última posición de `cmd` siempre
                se trata como salida, exista o no en esta lista.
            progress_time: Duración del tramo de vídeo a procesar.
            total_steps: Número de pasos esperados de `showinfo` por stderr.

        Raises:
            CommandError: Si falla el cmd o se bloquea.
            UserError: Si el usuario interrumpe la ejecución.
            OsError: Si no se puede mover una salida a su destino final.
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

        def _finish_readers() -> None:
            """Espera solo a los lectores iniciados antes de cerrar los pipes."""
            for thread in (stderr_thread, stdout_thread):
                if thread.ident is not None:
                    thread.join()
            if proc.stdout is not None:
                proc.stdout.close()
            if proc.stderr is not None:
                proc.stderr.close()

        def _abort(mode: _AbortMode) -> Never:
            """Detiene el proceso e informa; el temporal se descarta al salir."""
            if proc.poll() is None:
                proc.kill()
            proc.wait()
            _finish_readers()

            match mode:
                case _AbortMode.MANUAL:
                    raise UserError(
                        msg=_("FFmpeg command interrupted manually: %(command_name)s")
                        % {"command_name": self.command_name}
                    )
                case _AbortMode.TIMEOUT:
                    raise CommandError(
                        msg=_("FFmpeg command timed out: %(command_name)s")
                        % {"command_name": self.command_name}
                    )
                case _AbortMode.FFMPEG:
                    tail = "".join(stderr_lines[-10:]).strip()
                    detail = f"\nffmpeg stderr:\n{tail}" if tail else ""
                    raise CommandError(
                        msg=_("FFmpeg command failed during execution.") + detail
                    )

        # ffmpeg no debe preguntar por su cuenta (el prompt queda oculto tras la
        # barra de progreso y bloquea): la política ya se resolvió en el servicio.
        overwrite = getattr(getattr(self, "params", None), "overwrite", None)
        overwrite_yes = overwrite == OverwriteMode.YES
        if Path(cmd[0]).stem == "ffmpeg":
            cmd = [
                cmd[0],
                "-nostdin",
                "-y" if overwrite_yes else "-n",
                *(arg for arg in cmd[1:] if arg not in ("-y", "-n")),
            ]

        dest_dir = Path(cmd[-1]).parent
        # Mismo sistema de ficheros que el destino: `replace` es atómico. Si la
        # limpieza falla no debe enmascarar el error real que la provoca.
        with tempfile.TemporaryDirectory(
            dir=dest_dir, prefix=".pymedia-", ignore_cleanup_errors=True
        ) as tmp_dir:
            staging = Path(tmp_dir)
            cmd = self._stage_outputs(
                cmd=cmd, output_list={str(o) for o in output_list}, staging=staging
            )
            stderr_lines: list[str] = []
            events: queue.Queue[tuple[str, str | None]] = queue.Queue()
            stdout_thread = threading.Thread(target=_read_stdout, daemon=True)
            stderr_thread = threading.Thread(target=_read_stderr, daemon=True)
            proc = subprocess.Popen(
                args=cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.DEVNULL,
                text=True,
                errors="replace",
                bufsize=1,
            )

            try:
                assert proc.stdout is not None
                assert proc.stderr is not None
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
                        source, line = events.get(timeout=self.config.app.stall_timeout)
                        if line is None:
                            pending_streams.discard(source)
                            continue

                        if progress_time is not None and line.startswith(
                            "out_time_ms="
                        ):
                            value = line.partition("=")[2].strip()
                            if value.isdigit():
                                progress.update(
                                    task_id=task, completed=int(value) / 1_000_000
                                )
                        elif total_steps is not None and source == "stderr":
                            completed_steps += 1
                            progress.update(task_id=task, completed=completed_steps)

                    proc.wait()
                    _finish_readers()
                    if proc.returncode == 0 and total is not None:
                        progress.update(task_id=task, completed=total)
            except KeyboardInterrupt:
                _abort(mode=_AbortMode.MANUAL)
            except queue.Empty:
                _abort(mode=_AbortMode.TIMEOUT)

            if proc.returncode != 0:
                _abort(mode=_AbortMode.FFMPEG)

            self._commit_outputs(
                staging=staging, dest_dir=dest_dir, overwrite=overwrite_yes
            )

    @staticmethod
    def _stage_outputs(
        cmd: list[str], output_list: set[str], staging: Path
    ) -> list[str]:
        """Redirige al directorio temporal los argumentos de salida del comando."""
        # La salida principal (o su plantilla `%03d`) es siempre el último
        # argumento; `output_list` aporta el resto en comandos multisalida.
        targets = {cmd[-1], *output_list}
        return [
            str(staging / Path(arg).name) if index and arg in targets else arg
            for index, arg in enumerate(cmd)
        ]

    @staticmethod
    def _commit_outputs(staging: Path, dest_dir: Path, overwrite: bool) -> None:
        """Mueve las salidas completas del temporal a su destino final."""
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
