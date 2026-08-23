from dataclasses import dataclass
from datetime import timedelta
from pathlib import Path

from pymedia.errors import MissingArgumentError
from pymedia.logger import Logger
from pymedia.models.config import Config
from pymedia.models.enums import OverwriteMode
from pymedia.models.media import Media
from pymedia.services.parameter_service import (
    load_media,
    process_output,
    process_scale,
    process_time,
    validate_animated_output,
)

logger = Logger.load("gif_model")


@dataclass(frozen=True, kw_only=True, slots=True)
class GifArguments:
    """Parámetros utilizados por el comando GIF.

    input_single: Ruta del vídeo a procesar.
    output: Ruta del fichero de salida. [defecto: input.gif]
    overwrite: Indica actuación ante fichero de salida ya existente. [defecto: ask]
    fps: Número de imágenes por segundos. [defecto: 15]
    scale: Altura de fotograma para redimensionar el vídeo o la imagen. [defecto: 480]
    timestamp_start: Marca temporal que indica el punto inicial.
    timestamp_end: Marca temporal que indica el punto final.
    """

    input_single: Path
    output: Path | None
    overwrite: OverwriteMode
    fps: int
    scale: int
    timestamp_start: str | None
    timestamp_end: str | None


@dataclass(kw_only=True, slots=True)
class GifParameters:
    """Parámetros utilizados por el comando GIF.

    input_single: Ruta del vídeo a procesar.
    media: Metadatos del vídeo de entrada ya resuelto y validado.
    output: Ruta absoluta del fichero de salida.
    overwrite: Indica actuación ante fichero de salida ya existente. [defecto: ask]
    fps: Número de imágenes por segundos [defecto: 15].
    scale: Altura de fotograma para redimensionar el vídeo o la imagen [defecto: 480].
    timestamp_start: Marca temporal que indica el punto inicial.
    timestamp_end: Marca temporal que indica el punto final.
    """

    input_single: Path
    media: Media
    output: Path
    overwrite: OverwriteMode
    fps: int
    scale: int | None = None
    timestamp_start: timedelta | None = None
    timestamp_end: timedelta | None = None

    @classmethod
    def create(cls, args: GifArguments, config: Config) -> "GifParameters":

        if not args.input_single:
            raise MissingArgumentError(argument="input_single")

        media = load_media(args.input_single)

        output = process_output(
            input_single=args.input_single, output=args.output, extension=".gif"
        )

        validate_animated_output(output=output)

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
                time_str=args.timestamp_start,
                media=media,
            )
            if args.timestamp_start
            else None
        )

        timestamp_end = (
            process_time(
                time_str=args.timestamp_end,
                media=media,
            )
            if args.timestamp_end
            else None
        )

        return cls(
            input_single=args.input_single,
            media=media,
            output=output,
            overwrite=args.overwrite,
            fps=args.fps,
            scale=scale,
            timestamp_start=start_point,
            timestamp_end=timestamp_end,
        )
