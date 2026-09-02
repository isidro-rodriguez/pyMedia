"""Clases base de los subcomandos de la CLI de pyMedia.

Define el ciclo de vida común (carga de configuración, parseo de parámetros,
resolución de sobrescritura, construcción y ejecución de ffmpeg) para comandos
de fichero único y de procesamiento por lotes.
"""

import inspect
import queue
import subprocess
import threading
from abc import ABC, abstractmethod
from datetime import timedelta
from pathlib import Path
from typing import TypeVar

import typer
from rich.progress import Progress

from pymedia.data.types import OverwriteMode
from pymedia.errors import CommandError, MissingMediaPropertyError
from pymedia.locales import _  # noqa
from pymedia.logger import Logger
from pymedia.models.config import Config

ArgsT = TypeVar("ArgsT")
ParamsT = TypeVar("ParamsT")


class BaseCommand[ArgsT, ParamsT](ABC):
    """Clase abstracta que define la base de los comandos del programa.

    Attributes:
        name: Nombre del subcomando, usado para registro y ayuda en Typer.
        config: Configuración cargada de la aplicación.
        logger: Servicio de registro y almacén de mensajes.
        args: Argumentos ya tipados específicos del comando.
        params: Parámetros procesados a partir de `args`.
        cmd: Comando ffmpeg construido, listo para ejecutar.
    """

    name: str
    config: Config
    logger: Logger
    args: ArgsT
    params: ParamsT
    cmd: list[str]

    def __init__(self, args: ArgsT, config: Config) -> None:
        """Inicializa el comando con argumentos de tipo definido y la config cargada.

        Args:
            args: Argumentos ya tipados específicos del comando.
            config: Configuración cargada de la aplicación.
        """
        self.args = args
        self.config = config

    @staticmethod
    @abstractmethod
    def cli(*args, **kwargs) -> None:
        """Subcomando de cli para Typer y composición de la ayuda.

        Debe implementarse como `staticmethod`: Typer inspecciona la firma
        con `inspect.signature()` y no debe interpretar `self`/`cls` como
        una opción del comando.
        """
        pass

    @classmethod
    def build_args(cls, args_cls, local_vars: dict) -> ArgsT:
        """Recoge todos los argumentos de la lista de parámetros.

        Filtra `local_vars` quedándose solo con las claves que coinciden
        con los parámetros aceptados por `args_cls`.

        Args:
            args_cls: Clase de argumentos cuya firma define los campos válidos.
            local_vars: Variables locales del `cli()` invocante (`locals()`).

        Returns:
            Instancia de `args_cls` construida con los valores filtrados.
        """
        valid_params = inspect.signature(args_cls).parameters
        return args_cls(**{k: v for k, v in local_vars.items() if k in valid_params})

    @classmethod
    def register(cls, app: typer.Typer) -> None:
        """Registra el subcomando en la app Typer.

        Args:
            app: Instancia de la aplicación Typer donde se registra el comando.
        """
        app.command(name=cls.name, help=getattr(cls, "help", None))(cls.cli)

    @staticmethod
    def resolve_overwrite(params: ParamsT) -> bool:
        """Comprueba si el fichero de salida existe y resuelve la sobrescritura.

        Args:
            params: Parámetros del comando con el modo de sobrescritura.

        Returns:
            `True`: El proceso continuar con normalidad.
            `False`: El proceso termina.
        """
        if params.overwrite != OverwriteMode.ASK:
            return True
        if not params.output.exists():
            return True

        overwrite = typer.confirm(_("Output file already exists. Overwrite?"))
        if not overwrite:
            return False

        params.overwrite = OverwriteMode.YES
        return True

    @staticmethod
    def run_ffmpeg(
        cmd: list[str],
        description: str,
        stall_timeout: int,
        command_name: str,
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
            description: Mensaje ya traducido a mostrar junto a la barra.
            stall_timeout: Tiempo de espera en caso de comando ffmpeg bloqueado.
            command_name: Nombre interno del comando para los mensajes de error.
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
                msg=_("FFmpeg command timed out: %(name)s") % {"name": command_name}
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
                    source, line = events.get(timeout=stall_timeout)
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

        if proc.returncode != 0:
            raise CommandError(msg=_("FFmpeg command failed during execution."))

    @staticmethod
    def resolve_progress_time(
        video_duration: timedelta, start: timedelta | None, end: timedelta | None
    ) -> timedelta:
        """Resuelve la duración del tramo de vídeo a procesar.

        Calcula la duración del tramo de vídeo a procesar definido por los flags
        `--start`, `--end` y `media.duration` para que muestre correctamente el avance
        la barra de progreso de Rich.

        Args:
            video_duration: Duración del vídeo a procesar.
            start: String indicando punto inicial.
            end: String indicando punto final.

        Returns:
            Duración del tramo de vídeo a procesar.
        """
        if video_duration is None:
            raise MissingMediaPropertyError(name="duration")
        if start is not None and end is not None:
            return end - start
        if start is not None:
            return video_duration - start
        if end is not None:
            return video_duration - end
        return video_duration


class SingleCommand(BaseCommand[ArgsT, ParamsT], ABC):
    """Clase abstracta para comandos que procesan ficheros individualmente.

    Attributes:
        params: Parámetros para la generación del comando.
    """

    @abstractmethod
    def process_parameters(self) -> None:
        """Validación y parseo de argumentos (input_single) a atributos de comando."""
        pass

    @abstractmethod
    def process_cmd(self) -> None:
        """Preparación y obtención del cmd de ffmpeg."""
        pass

    @classmethod
    def run(cls, args: ArgsT, debug: bool) -> None:
        """Carga la config, instancia el comando y ejecuta el flujo de comando.

        Orquesta el ciclo completo: carga de configuración, inicialización
        del logger, instanciación y llamada secuencial a
        `process_attributes()`, `process_cmd()` y `execute_cmd()`.

        Args:
            args: Argumentos ya tipados específicos del comando.
            debug: Si `True`, habilita el nivel de log de depuración.
        """
        config = Config.load()
        cls.logger = Logger.load(debug=debug)
        instance = cls(args, config)
        instance.process_parameters()
        if not instance.resolve_overwrite(params=instance.params):
            cls.logger.warning(
                _("BaseCommand skipped since output file already exists.")
            )
            return
        instance.process_cmd()


class BatchCommand(BaseCommand[ArgsT, list[ParamsT]], ABC):
    """Clase abstracta para comandos con interés para procesamiento en masa.

    Attributes:
        params: Lista de parámetros para la generación del comando.
    """

    params: list[ParamsT]

    @abstractmethod
    def process_parameters(self, input_single: Path) -> ParamsT:
        """Validación y parseo de argumentos (input_single) a atributos de comando.

        Args:
            input_single: Ruta del fichero a procesar.
        """
        pass

    @abstractmethod
    def process_cmd(self, params: ParamsT) -> None:
        """Preparación y obtención del cmd de ffmpeg.

        Args:
            params: Parámetros parseados y validados con el tipo específico del comando.
        """
        pass

    @classmethod
    def run(cls, args: ArgsT, debug: bool) -> None:
        """Flujo para comandos que procesan varios ficheros.

        Orquesta el ciclo completo: carga de configuración, inicialización
        del logger, instanciación y llamada secuencial a
        `process_attributes()`, `process_cmd()` y `execute_cmd()`.

        Args:
            args: Argumentos ya tipados específicos del comando.
            debug: Si `True`, habilita el nivel de log de depuración.
        """
        config = Config.load()
        cls.logger = Logger.load(debug=debug)
        instance = cls(args, config)
        instance.params = []
        for input_single in args.input_list:
            params_single = instance.process_parameters(input_single=input_single)
            instance.params.append(params_single)
        for params_single in instance.params:
            if not instance.resolve_overwrite(params=params_single):
                cls.logger.warning(
                    _("BaseCommand skipped since output file already exists.")
                )
                continue
            instance.process_cmd(params=params_single)
