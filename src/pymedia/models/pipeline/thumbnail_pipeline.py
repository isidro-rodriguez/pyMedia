from dataclasses import dataclass
from pathlib import Path

from pymedia.data.types import OutputMediaType, OverwriteMode, RotateMode, ScaleMode
from pymedia.errors import (
    ExclusiveOptionsError,
    MissingRequiredOptionError,
)
from pymedia.logger import Logger
from pymedia.models.mixins.crop_mixin import CropMixin
from pymedia.models.mixins.flip_mixin import FlipMixin
from pymedia.models.mixins.fps_mixin import FpsImageMixin
from pymedia.models.mixins.image_mixin import ImageQualityMixin, SceneMixin
from pymedia.models.mixins.inputs_mixin import InputSingleMixin
from pymedia.models.mixins.outputs_mixin import OutputSingleMixin
from pymedia.models.mixins.rotate_mixin import RotateMixin
from pymedia.models.mixins.scale_mixin import ScaleMixin
from pymedia.models.mixins.timestamps_mixin import (
    TimestampAtMixin,
    TimestampEndMixin,
    TimestampStartMixin,
)


@dataclass(frozen=True, slots=True, kw_only=True)
class ThumbnailArguments:
    """Argumentos crudos del subcomando thumbnail, tal como llegan de la CLI.

    Attributes:
        input_single: Ruta del vídeo de entrada.
        output: Ruta de salida deseada, o None para usar la derivada de
            input_single.
        overwrite: Política de sobrescritura de archivos existentes.
        every: Intervalo en segundos entre thumbnails (modo intervalo).
        scene: Umbral de sensibilidad para detección de cambio de escena
            (modo escena).
        timestamp_at: Marca o marcas de tiempo, sin parsear, para capturar
            thumbnails puntuales (modo timestamp).
        timestamp_start: Inicio del rango temporal a procesar, sin parsear.
        timestamp_end: Fin del rango temporal a procesar, sin parsear.
        crop: Especificación de corte, sin parsear.
        scale_to: Dimensiones de escalado destino, sin parsear.
        scale_mode: Modo de escalado a aplicar (STRETCH, FIT, COVER).
        scale_upscale: Si se permite escalar por encima del tamaño original.
        hflip: Si se aplica volteo horizontal.
        vflip: Si se aplica volteo vertical.
        rotate: Modo de rotación a aplicar, o None si no se rota.
    """

    input_single: Path
    output: Path | None = None
    overwrite: OverwriteMode
    every: int | None = None
    scene: float | None = None
    timestamp_at: str | None = None
    timestamp_start: str | None
    timestamp_end: str | None
    crop: str | None = None
    scale_to: str | None = None
    scale_mode: ScaleMode = ScaleMode.FIT
    scale_upscale: bool = False
    hflip: bool = False
    vflip: bool = False
    rotate: RotateMode | None = None


@dataclass(kw_only=True)
class ThumbnailParameters(
    InputSingleMixin,
    OutputSingleMixin,
    ImageQualityMixin,
    TimestampAtMixin,
    TimestampStartMixin,
    TimestampEndMixin,
    SceneMixin,
    FpsImageMixin,
    CropMixin,
    ScaleMixin,
    FlipMixin,
    RotateMixin,
):
    """Parámetros validados y parseados para generar thumbnails.

    Se construye exclusivamente a través de create(), que valida y parsea
    los ThumbnailArguments crudos de la CLI en los tipos que consumen
    thumbnail_cmd.

    Attributes:
        input_single: Ruta del fichero de vídeo a procesar.
        media: Metadatos del vídeo.
        output: Ruta del fichero de salida procesada
        overwrite: Política de sobrescritura de archivos existentes.
        timestamp_at: Lista de marcas de tiempo indicando las capturas de thumbnails.
        timestamp_start: Marca de tiempo que indica el punto inicial.
        timestamp_end: Marca de tiempo que indica el punto final.
        scene: Índice de sensibilidad de cambio de fotograma para obtener imagen.
        fps: Frecuencia de extracción en segundos por imagen.
        crop_area: Área y coordenada de la zona a preservar de la imagen.
        scale_mode: Política de escalado del vídeo o imagen.
        scale_upscale: Permite el incremento de dimensiones.
        scale_to: Dimensiones objetivo a las que se va a escalar el vídeo o imagen.
        hflip: Invierte la imagen horizontalmente, intercambiando izquierda y derecha.
        vflip: Invierte la imagen verticalmente, intercambiando arriba y abajo.
        rotate: Ángulo de rotación que se va a someter el vídeo.
    """

    overwrite: OverwriteMode

    @classmethod
    def create(cls, args: ThumbnailArguments, logger: Logger) -> "ThumbnailParameters":
        """Valida y parsea los argumentos crudos de la CLI a ThumbnailParameters.

        Args:
            args: Argumentos sin procesar recibidos del subcomando thumbnail.
            logger: Logger compartido para reportar avisos durante el parseo.

        Returns:
            Instancia de ThumbnailParameters lista para thumbnail_cmd.

        Raises:
            MissingRequiredOptionError: Si no se aporta ninguna de --at,
                --scene o --every.
            ExclusiveOptionsError: Si se combinan opciones incompatibles
                entre sí (--at/--scene/--every, o --at con --start/--end).
        """

        params = cls(
            overwrite=args.overwrite,
            scale_mode=args.scale_mode,
            hflip=args.hflip,
            vflip=args.vflip,
        )

        params.create_input_single(
            input_single=args.input_single,
            logger=logger,
        )

        params.create_output_single(
            media_type=OutputMediaType.IMAGE,
            output=args.output,
            affix="_thumbnail",
            extension=".jpg",
        )

        if args.timestamp_at is not None:
            params.create_timestamp_at(
                times_str=args.timestamp_at,
            )

        if args.timestamp_start is not None:
            params.create_timestamp_start(
                start=args.timestamp_start,
            )

        if args.timestamp_end is not None:
            params.create_timestamp_end(
                end=args.timestamp_end,
            )

        if args.scene is not None:
            params.create_scene(
                scene=args.scene,
            )

        if args.every is not None:
            params.create_fps(
                every=args.every,
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

        if args.rotate is not None:
            params.create_rotate(
                rotate=args.rotate,
            )

        _validate_options(params=params)

        return params


def _validate_options(params: ThumbnailParameters) -> None:
    """Verifica que se han aportado opciones requeridas y que no se han introducido
    combinaciones ambiguas."""
    at, scene, fps = params.timestamp_at, params.scene, params.fps
    start, end = params.timestamp_start, params.timestamp_end

    # 1. Al menos uno debe existir (evaluando presencia explícita)
    if not any(x is not None for x in (at, scene, fps)):
        raise MissingRequiredOptionError(options=["--at", "--scene", "--every"])

    # 2. Exclusividad mutua (máximo 1 de las opciones principales)
    if sum(x is not None for x in (at, scene, fps)) > 1:
        raise ExclusiveOptionsError(options=["--at", "--scene", "--every"])

    # 3. Conflicto entre --at y rango (--start / --end)
    if at is not None and any(x is not None for x in (start, end)):
        raise ExclusiveOptionsError(
            option="--at", incompatible_with=["--start", "--end"]
        )

    # 4. Validación de orden si existe el rango completo
    if start is not None and end is not None:
        params.validate_timestamp_start_order(time=end)
