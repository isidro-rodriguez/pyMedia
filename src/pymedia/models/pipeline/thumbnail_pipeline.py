from dataclasses import dataclass
from pathlib import Path

from pymedia.errors import (
    ConflictiveOptionsError,
    MissingRequiredOptionError,
)
from pymedia.logger import Logger
from pymedia.models.enums import OutputMediaType, OverwriteMode, RotateMode, ScaleMode
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
    overwrite: OverwriteMode

    @classmethod
    def create(cls, args: ThumbnailArguments, logger: Logger) -> "ThumbnailParameters":
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
        raise ConflictiveOptionsError(options=["--at", "--scene", "--every"])

    # 3. Conflicto entre --at y rango (--start / --end)
    if at is not None and any(x is not None for x in (start, end)):
        raise ConflictiveOptionsError(
            option="--at", incompatible_with=["--start", "--end"]
        )

    # 4. Validación de orden si existe el rango completo
    if start is not None and end is not None:
        params.validate_timestamp_start_order(time=end)
