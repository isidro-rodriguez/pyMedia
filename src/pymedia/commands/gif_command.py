from pymedia import locales
from pymedia.errors import CommandGenerationError
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.models.gif_model import GifParameters
from pymedia.services.command_service import (
    resolve_output_conflict,
    run_ffmpeg,
)

logger = Logger.load("gif")


def gif_command(config: Config, params: GifParameters) -> None:
    """
    Proceso de generación de cmd ffmpeg y ejecución.

    Args:
        config: Configuración de la aplicación.
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.

    Raises:
        CommandGenerationError: Si no se ha podido generar el comando ffmpeg.

    Warnings:
        skip_on_conflit: Si el fichero de salida ya existe y se ha activado
                la opción de resolver conflicto mediante SKIP.
    """

    output = resolve_output_conflict(
        output=params.output,
        output_on_conflict=params.output_on_conflict,
        logger=logger,
    )

    if output is None:
        logger.warning(key="skip_on_conflit", file_path=params.output)
        return

    params.output = output

    cmd = gif_cmd(params=params)

    if cmd is None:
        raise CommandGenerationError(command_name="gif")

    logger.debug(key="ffmpeg_command", cmd=cmd)

    run_ffmpeg(
        cmd=cmd,
        duration=params.media.duration,
        description=locales.Progress["gif"],
    )

    logger.info(key="gif_success", output=params.output)
