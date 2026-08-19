from dataclasses import dataclass
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
)


@dataclass(frozen=True, slots=True, kw_only=True)
class EncodeParameters(BaseParameters):
    """
    Modelo de parámetros para el comando ENCODE.

    Attributes:
        crop: Márgenes de recorte a aplicar, si se especifican.
        gyrate: Modo de rotación del vídeo, si se especifica.
        media: Lista de metadatos de los vídeos a procesar.
        remux: Si se debe remuxear en lugar de recodificar.
        scale: Modo de escalado de vídeo, si se especifica.
    """

    crop: list[CropMargins] | None = None
    gyrate: GyrateMode | None = None
    media: list[Media]
    remux: bool = False
    scale: list[ScaleVideoMode | None] | None = None

    @classmethod
    def create(cls, args: Arguments, config: Config) -> "EncodeParameters":
        """
        Construye los parámetros del comando ENCODE desde la entrada de la CLI.

        Args:
            args: Argumentos ya parseados por Typer.
            config: Configuración de la aplicación.

        Returns:
            Instancia de EncodeParameters lista para usar.

        Raises:
            MissingArgumentError: Si falta `inputs`.
        """

        if not args.inputs:
            raise MissingArgumentError(argument="inputs")

        media = load_media(args.inputs)

        crop = process_crop(crop=args.crop, media=media) if args.crop else None
        output = (
            process_output(
                output=args.output, command=CommandMode.ENCODE, config=config
            )
            if args.output
            else None
        )
        scale = (
            process_scale(
                scale=cast(ScaleVideoMode, args.scale), media=media, config=config
            )
            if args.scale
            else None
        )

        return cls(
            crop=crop,
            debug=args.debug,
            gyrate=args.gyrate,
            media=media,
            output=output,
            output_on_conflict=args.output_on_conflict,
            remux=args.remux,
            scale=scale,
        )
