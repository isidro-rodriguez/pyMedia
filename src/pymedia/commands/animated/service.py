"""Comando ``animated``: service."""

from pymedia.commands.animated.cmd import AnimatedCmd
from pymedia.commands.animated.parameters import AnimatedParameters
from pymedia.commands.base_service import BaseService
from pymedia.errors import (
    MissingParameterError,
)
from pymedia.locales import _


class AnimatedService(BaseService[AnimatedParameters]):
    """Comando de CLI que genera una imagen animada desde el vídeo de entrada."""

    def start(self) -> None:
        """Construye el comando ffmpeg y ejecuta la generación de una imagen animada.

        Raises:
            MissingParameterError: Si no se obtuvo el medio o la salida animada.
        """
        if self.params.media is None:
            raise MissingParameterError(name="media")
        if self.params.animated_output is None:
            raise MissingParameterError(name="animated_output")

        if not self.resolve_overwrite(output_list=[self.params.animated_output]):
            return

        cmd = AnimatedCmd(params=self.params).create()

        self.logger.debug(_("FFmpeg command: %(cmd)s"), cmd=cmd)

        self.run_ffmpeg(
            cmd=cmd,
            description=_("Generating animated image"),
            progress_time=self.params.get_range_time(),
            output_list=[self.params.animated_output],
        )

        self.logger.info(
            msg=_("Animated image generated successfully: %(output)s"),
            output=self.params.animated_output,
        )
