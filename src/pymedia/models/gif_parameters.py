from dataclasses import dataclass
from datetime import timedelta
from typing import cast

from pymedia.errors import MissingArgumentError
from pymedia.models.arguments import Arguments
from pymedia.models.base_parameters import (
    BaseParameters,
    CommandMode,
    CropMargins,
    GyrateMode,
    ScaleGifMode,
)
from pymedia.models.config import Config
from pymedia.models.media import Media
from pymedia.services.parameter_service import (
    load_media,
    process_crop,
    process_output,
    process_scale,
    process_time,
)


@dataclass(slots=True, kw_only=True)
class GifParameters(BaseParameters):
    """
    Modelo de parámetros para el comando GIF.

    Attributes:
        crop: Márgenes de recorte a aplicar, si se especifican.
        end_point: Marca temporal que indica el punto final del Gif.
        fps: Número de imágenes por segundo del Gif.
        gyrate: Modo de rotación del vídeo, si se especifica.
        media: Metadatos del vídeo de entrada ya resuelto y validado.
        scale: Modo de escalado de vídeo, si se especifica.
        start_point: Marca temporal que indica el punto inicial del Gif.
    """

    crop: CropMargins | None = None
    end_point: timedelta | None = None
    fps: int
    gyrate: GyrateMode | None = None
    media: Media
    scale: ScaleGifMode
    start_point: timedelta | None = None

    @classmethod
    def create(cls, args: Arguments, config: Config) -> "GifParameters":
        """Construye los parámetros del comando GIF desde la entrada de la CLI.

        Args:
            args: Argumentos ya parseados por Typer.
            config: Configuración de la aplicación.

        Returns:
            Instancia de GifParameters lista para usar.

        Raises:
            MissingArgumentError: Si falta `inputs`.
        """

        if not args.inputs:
            raise MissingArgumentError(argument="inputs")

        media = load_media(args.inputs)[0]

        crop = (
            process_crop(
                crop=args.crop,
                media=[media],
            )[0]
            if args.crop
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

        if args.fps:
            fps = args.fps
        else:
            raise MissingArgumentError(argument="fps")

        output = (
            process_output(
                output=args.output,
                command=CommandMode.GIF,
                config=config,
                media=[media],
            ).absolute()
            if args.output
            else args.inputs[0].with_suffix(".gif").absolute()
        )

        if args.scale:
            scale = process_scale(
                scale=cast(ScaleGifMode, args.scale), media=[media], config=config
            )[0]
        else:
            raise MissingArgumentError(argument="scale")
        if scale is None:
            raise MissingArgumentError(argument="scale")

        start_point = (
            process_time(
                time_str=args.start_point,
                media=media,
            )
            if args.start_point
            else None
        )

        return cls(
            crop=crop,
            debug=args.debug,
            end_point=end_point,
            fps=fps,
            gyrate=args.gyrate,
            media=media,
            output=output,
            output_on_conflict=args.output_on_conflict,
            scale=scale,
            start_point=start_point,
        )
