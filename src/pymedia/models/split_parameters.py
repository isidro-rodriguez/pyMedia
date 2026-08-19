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
    ScaleVideoMode,
)
from pymedia.models.config import Config
from pymedia.models.media import Media
from pymedia.services.parameter_service import (
    load_media,
    process_crop,
    process_output,
    process_scale,
    process_trim_points,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class SplitParameters(BaseParameters):
    """
    Modelo de parámetros para el comando SPLIT.

    Attributes:
        crop: Márgenes de recorte a aplicar, si se especifican.
        gyrate: Modo de rotación del vídeo, si se especifica.
        media: Vídeo de entrada ya resuelto y validado.
        remux: Si se debe remuxear en lugar de recodificar.
        scale: Modo de escalado de vídeo, si se especifica.
        trim_points: Puntos de corte para dividir el vídeo.
    """

    crop: CropMargins | None = None
    gyrate: GyrateMode | None = None
    media: Media | None = None
    remux: bool = False
    scale: ScaleVideoMode | None = None
    trim_points: list[timedelta]

    @classmethod
    def create(cls, args: Arguments, config: Config) -> "SplitParameters":
        """
        Construye los parámetros del comando SPLIT desde la entrada de la CLI.

        Args:
            args: Argumentos ya parseados por Typer.
            config: Configuración de la aplicación.

        Returns:
            Instancia de SplitParameters lista para usar.

        Raises:
            MissingArgumentError: Si falta `inputs` o `trim_points`.
        """

        if not args.inputs:
            raise MissingArgumentError(argument="inputs")

        media = load_media(args.inputs)[0]

        crop = process_crop(crop=args.crop, media=[media])[0] if args.crop else None
        output = (
            process_output(output=args.output, command=CommandMode.SPLIT, config=config)
            if args.output
            else None
        )
        scale = (
            process_scale(
                scale=cast(ScaleVideoMode, args.scale), media=[media], config=config
            )[0]
            if args.scale
            else None
        )

        if args.trim_points is None:
            raise MissingArgumentError(argument="trim_points")
        trim_points = process_trim_points(trim_points_str=args.trim_points, media=media)

        return cls(
            crop=crop,
            debug=args.debug,
            gyrate=args.gyrate,
            media=media,
            output=output,
            output_on_conflict=args.output_on_conflict,
            remux=args.remux,
            scale=scale,
            trim_points=trim_points,
        )
