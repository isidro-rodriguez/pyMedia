from pymedia import locales
from pymedia.errors import CommandGenerationError
from pymedia.ffmpeg.gif_cmd import gif_cmd
from pymedia.logger import get_logger, log_debug, log_info, log_warning
from pymedia.models.gif_parameters import GifParameters
from pymedia.services.command_service import (
    resolve_output_conflict,
    run_ffmpeg,
)

logger = get_logger("gif")


def gif_command(params: GifParameters) -> None:
    """
    Proceso de generación de cmd ffmpeg y ejecución.

    Args:
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.

    Returns:
        Fin de aplicación.

    Raises:
        CommandGenerationError: Si no se ha podido generar el comando ffmpeg.

    Warnings:
        skip_on_conflit: Si el fichero de salida ya existe y se ha activado
                la opción de resolver conflicto mediante SKIP.
    """

    output_tmp = resolve_output_conflict(
        output=params.output,
        output_on_conflict=params.output_on_conflict,
        logger=logger,
    )

    if output_tmp is None:
        log_warning(logger=logger, key="skip_on_conflit", file_path=params.output)
        return

    params.output = output_tmp

    cmd = gif_cmd(params=params)

    if cmd is None:
        raise CommandGenerationError(command_name="gif")

    log_debug(logger, "ffmpeg_command", cmd=cmd)

    run_ffmpeg(
        cmd=cmd,
        duration=params.media.duration,
        description=locales.Progress["gif"],
    )

    log_info(logger, "gif_success", output=params.output)
