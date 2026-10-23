"""Comando ``play``: service."""

import shutil
import subprocess

from pymedia.commands.base.service import BaseService
from pymedia.commands.play.cmd import PlayCmd
from pymedia.commands.play.parameters import PlayParameters
from pymedia.errors import CommandError, MissingParameterError, UserError
from pymedia.locales import translate as _


class PlayService(BaseService[PlayParameters]):
    """Comando de CLI para reproducir un vídeo con ffplay."""

    def start(self) -> None:
        """Construye el comando ffplay y abre la ventana de reproducción.

        La reproducción es interactiva: ffplay recibe el teclado y su salida va
        directamente a la terminal, sin barra de progreso.

        Raises:
            MissingParameterError: Si no se pudo obtener el medio de entrada.
            UserError: Si ffplay no está en el `PATH`.
            CommandError: Si ffplay termina con error.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")

        cmd = PlayCmd(params=self.params).create()

        self.display_cmd(cmd=cmd)

        # Solo `play` necesita ffplay: no se exige al arrancar la aplicación.
        binary = shutil.which(cmd[0])
        if binary is None:
            raise UserError(
                msg=_("%(binary)s was not found in PATH. Install ffmpeg first.")
                % {"binary": cmd[0]}
            )

        self.logger.info(msg=_("Playing %(name)s"), name=self.params.media.path.name)
        try:
            result = subprocess.run([binary, *cmd[1:]], check=False)
        except KeyboardInterrupt:
            # Ctrl+C también llega a ffplay, que cierra la ventana.
            return

        if result.returncode != 0:
            raise CommandError(
                msg=_("ffplay ended with an error (exit code %(code)s).")
                % {"code": result.returncode}
            )
