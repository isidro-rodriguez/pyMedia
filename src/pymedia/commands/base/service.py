"""Clases base de los servicios de pyMedia.

Define los servicios comunes para los comandos.
"""

import os
import re
import shlex
from abc import ABC
from collections.abc import Iterable
from datetime import timedelta
from pathlib import Path
from typing import Protocol, TypeVar

import typer
from rich.text import Text

from pymedia.commands.base.ffmpeg_runner import run_ffmpeg
from pymedia.errors import (
    InvalidParameterError,
)
from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.types import OverwriteMode
from pymedia.ui import confirm


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
            proceso debe omitirse. Con `--show-cmd` no se pregunta: no se
            escribe nada.

        Raises:
            typer.Abort: Si el usuario cierra la entrada sin responder.
        """
        params = self.params
        if params.overwrite == OverwriteMode.YES or self.show_cmd:
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
                if confirm(_("Overwrite?")):
                    params.overwrite = OverwriteMode.YES
                    return True
                self.logger.warning(process_skip_msg)
                return False
        return True

    def display_cmd(self, cmd: list[str]) -> None:
        """Muestra el comando compuesto al usuario si ha activado debug o show-cmd.

        Args:
            cmd: Comando ffmpeg ya construido.

        Raises:
            typer.Exit: Tras mostrar el comando con `show_cmd`, o si el usuario
                rechaza ejecutarlo en modo debug.
        """
        if self.show_cmd:
            self.logger.print(renderable=format_cmd(cmd), emoji=False, soft_wrap=True)
            raise typer.Exit()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        if self.debug and not confirm(_("Do you want to run this ffmpeg command?")):
            self.logger.warning(msg=_("User decided to abort process."))
            raise typer.Exit()

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
            InvalidParameterError: Si dos salidas comparten nombre de fichero.
            OperativeSystemError: Si el directorio de destino no existe o no se
                puede mover una salida a su destino final.
        """
        run_ffmpeg(
            cmd=cmd,
            description=description,
            outputs=output_list,
            overwrite=self.params.overwrite == OverwriteMode.YES,
            stall_timeout=self.config.app.stall_timeout,
            command_name=self.command_name,
            progress_time=progress_time,
            total_steps=total_steps,
        )


def format_cmd(cmd: list[str]) -> Text:
    """Formatea el comando para copiarlo en la shell, coloreado por tipo de token.

    Los tokens se entrecomillan según el sistema operativo; el color no altera
    el texto, que sigue siendo válido al copiarlo.

    Args:
        cmd: Comando ffmpeg ya construido.

    Returns:
        Texto con el binario, las opciones, las rutas y los valores resaltados,
        precedido y seguido de un salto de línea.
    """
    text = Text("\n")
    for index, token in enumerate(cmd):
        if index:
            text.append(" ")
        text.append(_quote_token(token), style=_token_style(index, token))
    text.append("\n")
    return text


def _quote_token(token: str) -> str:
    """Entrecomilla un token para la shell del sistema operativo."""
    if os.name != "nt":
        return shlex.quote(token)
    if not _UNSAFE_CHARS.search(token):
        return token
    return '"' + token.replace('"', '\\"') + '"'


def _token_style(index: int, token: str) -> str:
    """Estilo del token: binario, opción, ruta o valor."""
    if index == 0:
        return "cmd.binary"
    if re.match(r"^-[A-Za-z]", token):
        return "cmd.flag"
    if "/" in token or "\\" in token or Path(token).suffix:
        return "cmd.path"
    return "cmd.value"
