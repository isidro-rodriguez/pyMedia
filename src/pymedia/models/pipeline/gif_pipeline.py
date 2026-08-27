from dataclasses import dataclass
from pathlib import Path

from pymedia.logger import Logger
from pymedia.models.enums import OutputMediaType, OverwriteMode
from pymedia.models.mixins.fps_mixin import FpsGifMixin
from pymedia.models.mixins.inputs_mixin import InputSingleMixin
from pymedia.models.mixins.outputs_mixin import OutputSingleMixin
from pymedia.models.mixins.resize_mixin import ResizeMixin
from pymedia.models.mixins.timestamps_mixin import (
    TimestampEndMixin,
    TimestampStartMixin,
)


@dataclass(frozen=True, kw_only=True, slots=True)
class GifArguments:
    """Argumentos cargados por Typer para el comando GIF.

    Attributes:
        input_list: Lista de rutas de los vídeos a procesar.
        output: Ruta del fichero de salida. [defecto: INPUT_SINGLE.gif]
        overwrite: Indica actuación ante fichero de salida ya existente. [defecto: ask]
        fps: Número de imágenes por segundos. [defecto: 15]
        resize_width: Ancho objetivo para redimensionado.
        resize_height: Altura objetivo para redimensionado.
        resize_upscale: Permite el incremento de resolución.
        timestamp_start: Marca temporal que indica el punto inicial.
        timestamp_end: Marca temporal que indica el punto final.
    """

    input_list: list[Path]
    output: Path | None
    overwrite: OverwriteMode
    fps: int
    resize_width: int | None
    resize_height: int | None
    resize_upscale: bool
    timestamp_start: str | None
    timestamp_end: str | None


@dataclass(kw_only=True)
class GifParameters(
    InputSingleMixin,
    OutputSingleMixin,
    FpsGifMixin,
    ResizeMixin,
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
        resize_width: Ancho objetivo para redimensionado.
        resize_height: Altura objetivo para redimensionado.
        resize_upscale: Permite el incremento de resolución.
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

        params = cls(overwrite=args.overwrite)
        params.create_input_single(input_single=args.input_single, logger=logger)
        params.create_output_single(
            media_type=OutputMediaType.GIF, output=args.output, extension=".gif"
        )
        params.create_fps(fps=args.fps)
        params.create_resize(
            logger=logger,
            width=args.resize_width,
            height=args.resize_height,
            upscale=args.resize_upscale,
        )
        params.create_timestamp_start(start=args.timestamp_start)
        params.create_timestamp_end(end=args.timestamp_end)
        return params
