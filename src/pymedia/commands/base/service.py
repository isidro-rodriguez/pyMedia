"""Clases base de los servicios de pyMedia.

Define los servicios comunes para los comandos.
"""

import os
import re
import shlex
import sys
from abc import ABC
from collections.abc import Iterable
from datetime import timedelta
from pathlib import Path
from typing import Protocol, TypeVar

import typer

from pymedia.commands.base.ffmpeg_runner import run_ffmpeg
from pymedia.errors import (
    InvalidParameterError,
)
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.types import OverwriteMode


class _OverwriteParams(Protocol):
    """Parámetros capaces de resolver la sobrescritura de ficheros de salida."""

    overwrite: OverwriteMode


_UNSAFE_CHARS = re.compile(r"[^\w@%+=:,./-]")


ParamsT = TypeVar("ParamsT")


class BaseService[ParamsT: _OverwriteParams](ABC):
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
        params = self.params
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

        def _format_cmd() -> str:
            """Format a command list as a copy-pasteable shell string."""
            if os.name == "nt":
                return " ".join(_quote_windows(t) for t in cmd)
            return shlex.join(cmd)

        if self.show_cmd:
            self.logger.print(
                renderable=f"\n{_format_cmd()}\n",
                emoji=False,
                soft_wrap=True,
                markup=False,
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

        Delega en `ffmpeg_runner.run_ffmpeg` aportando la configuración del servicio.

        Args:
            cmd: Comando ffmpeg ya construido, listo para ejecutar.
            description: Mensaje a mostrar junto a la barra de progreso.
            output_list: Ficheros de salida que recibe `cmd` como argumento.
            progress_time: Duración del tramo de vídeo a procesar.
            total_steps: Número de pasos esperados de `showinfo` por stderr.

        Raises:
            CommandError: Si falla el cmd o se bloquea.
            UserError: Si el usuario interrumpe la ejecución.
            OperativeSystemError: Si no se puede mover una salida a su destino final.
        """
        overwrite = True if self.params.overwrite == OverwriteMode.YES else False
        run_ffmpeg(
            cmd=cmd,
            description=description,
            outputs=output_list,
            overwrite=overwrite,
            stall_timeout=self.config.app.stall_timeout,
            command_name=self.command_name,
            progress_time=progress_time,
            total_steps=total_steps,
        )
