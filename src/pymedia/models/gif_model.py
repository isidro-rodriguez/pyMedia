from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from pymedia.errors import MissingArgumentError
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.models.enums import CommandMode, OutputOnConflictMode
from pymedia.models.media import Media
from pymedia.services.parameter_service import (
    load_media,
    process_output,
    process_scale,
    process_time,
    validate_output,
)

logger = Logger.load("gif_model")


@dataclass(frozen=True, kw_only=True, slots=True)
class GifArguments:
    """
    Parámetros utilizados por el comando GIF.

    input_single: Ruta del vídeo a procesar.
    output: Ruta del fichero de salida.
    output_on_conflict: Actuación en caso de ficheros de salida ya existentes.
    fps: Número de imágenes por segundos [defecto: 15].
    scale: Altura de fotograma para redimensionar el vídeo o la imagen [defecto: 480].
    start_point: Marca temporal que indica el punto inicial.
    end_point: Marca temporal que indica el punto final.
    """

    input_single: Path
    output: Path | None
    output_on_conflict: OutputOnConflictMode
    fps: int
    scale: int
    start_point: str | None = None
    end_point: str | None = None


@dataclass(kw_only=True, slots=True)
class GifParameters:
    """
    Parámetros utilizados por el comando GIF.

    media: Metadatos del vídeo de entrada ya resuelto y validado.
    output: Ruta absoluta del fichero de salida.
    output_on_conflict: Actuación en caso de ficheros de salida ya existentes.
    fps: Número de imágenes por segundos [defecto: 15].
    scale: Altura de fotograma para redimensionar el vídeo o la imagen [defecto: 480].
    start_point: Marca temporal que indica el punto inicial.
    end_point: Marca temporal que indica el punto final.
    """

    media: Media
    output: Path
    output_on_conflict: OutputOnConflictMode
    fps: int
    scale: int | None = None
    end_point: timedelta | None = None
    start_point: timedelta | None = None

    @classmethod
    def create(cls, args: GifArguments, config: Config) -> "GifParameters":

        if not args.input_single:
            raise MissingArgumentError(argument="input_single")

        media = load_media(args.input_single)

        output = process_output(
            command=CommandMode.GIF, media=media, output=args.output
        )

        validate_output(
            output=output, command=CommandMode.GIF, config=config, media=media
        )

        scale = (
            process_scale(
                config=config,
                logger=logger,
                media=media,
                scale=args.scale,
            )
            if args.scale
            else None
        )

        start_point = (
            process_time(
                time_str=args.start_point,
                media=media,
            )
            if args.start_point
            else None
        )

        end_point = (
            process_time(
                time_str=args.end_point,
                media=media,
            )
            if args.end_point
            else None
        )

        return cls(
            media=media,
            output=output,
            output_on_conflict=args.output_on_conflict,
            fps=args.fps,
            scale=scale,
            start_point=start_point,
            end_point=end_point,
        )
