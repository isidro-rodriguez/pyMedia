from dataclasses import dataclass
from pathlib import Path

from pymedia.logger import Logger
from pymedia.models.enums import OutputMediaType, OverwriteMode, ScaleMode
from pymedia.models.mixins.crop_mixin import CropMixin
from pymedia.models.mixins.fps_mixin import FpsGifMixin
from pymedia.models.mixins.inputs_mixin import InputSingleMixin
from pymedia.models.mixins.outputs_mixin import OutputSingleMixin
from pymedia.models.mixins.scale_mixin import ScaleMixin
from pymedia.models.mixins.timestamps_mixin import (
    TimestampEndMixin,
    TimestampStartMixin,
)


@dataclass(frozen=True, kw_only=True, slots=True)
class GifArguments:
    """Argumentos cargados por Typer para el comando GIF.

    Attributes:
        input_single: Ruta al fichero a procesar.
        output: Ruta del fichero de salida. [defecto: INPUT_SINGLE.gif]
        overwrite: Indica actuación ante fichero de salida ya existente. [defecto: ask]
        fps: Número de imágenes por segundos. [defecto: 15]
        scale_to: Dimensión objetivo a re-escalar.
        scale_mode: Modo de re-escalado.
        scale_upscale: Permite el incremento de resolución.
        timestamp_start: Marca temporal que indica el punto inicial.
        timestamp_end: Marca temporal que indica el punto final.
    """

    input_single: Path
    output: Path | None
    overwrite: OverwriteMode
    fps: int
    crop: str | None
    scale_to: str
    scale_mode: ScaleMode
    scale_upscale: bool = False
    timestamp_start: str | None
    timestamp_end: str | None


@dataclass(kw_only=True)
class GifParameters(
    InputSingleMixin,
    OutputSingleMixin,
    CropMixin,
    ScaleMixin,
    FpsGifMixin,
    TimestampStartMixin,
    TimestampEndMixin,
):
    """Parámetros utilizados por el comando GIF.

    Attributes:
        input_single: Ruta del vídeo a procesar.
        media: Metadatos del vídeo de entrada ya resuelto y validado.
        output: Ruta absoluta del fichero de salida.
        overwrite: Indica actuación ante fichero de salida ya existente. [defecto: ask]
        fps: Número de imágenes por segundos [defecto: 15].
        scale_to: Ancho objetivo para redimensionado.
        timestamp_start: Marca temporal que indica el punto inicial.
        timestamp_end: Marca temporal que indica el punto final.
    """

    overwrite: OverwriteMode

    @classmethod
    def create(cls, args: GifArguments, logger: Logger) -> "GifParameters":
        """Crea y valida los parámetros del comando GIF desde de los argumentos brutos.

        Args:
            args: Argumentos crudos recibidos desde la CLI.
            logger: Logger para trazas de progreso.

        Returns:
            Instancia de GifParameters completamente inicializada.
        """

        params = cls(
            overwrite=args.overwrite,
            scale_mode=args.scale_mode,
        )

        params.create_input_single(
            input_single=args.input_single,
            logger=logger,
        )

        params.create_output_single(
            media_type=OutputMediaType.GIF,
            output=args.output,
            extension=".gif",
        )

        params.create_fps(
            fps=args.fps,
        )

        if args.crop is not None:
            params.create_crop(
                crop_str=args.crop,
            )

        if args.scale_to is not None:
            params.create_scale(
                logger=logger,
                scale_upscale=args.scale_upscale,
                scale_to=args.scale_to,
            )

        if args.timestamp_start is not None:
            params.create_timestamp_start(
                start=args.timestamp_start,
            )

        if args.timestamp_end is not None:
            params.create_timestamp_end(
                end=args.timestamp_end,
            )

        if params.timestamp_start is not None and params.timestamp_end is not None:
            params.validate_timestamp_start_order(time=params.timestamp_end)

        return params
