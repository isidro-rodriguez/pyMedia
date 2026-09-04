"""Modelos de parámetros de pipelines."""

from abc import ABC
from dataclasses import dataclass

from pymedia.models.mixins.crop_mixin import CropMixin
from pymedia.models.mixins.flip_mixin import FlipMixin
from pymedia.models.mixins.fps_mixin import FpsGifMixin, FpsImageMixin
from pymedia.models.mixins.image_mixin import ImageQualityMixin, SceneMixin
from pymedia.models.mixins.inputs_mixin import InputSingleMixin
from pymedia.models.mixins.outputs_mixin import OutputBatchMixin, OutputSingleMixin
from pymedia.models.mixins.rotate_mixin import RotateMixin
from pymedia.models.mixins.scale_mixin import ScaleMixin
from pymedia.models.mixins.sheet_presets_mixin import SheetPresetsMixin
from pymedia.models.mixins.timestamps_mixin import (
    TimestampAtMixin,
    TimestampStartEndMixin,
)
from pymedia.types import OverwriteMode


@dataclass(kw_only=True)
class BaseParameters(ABC):
    """Base para los dataclasses de parámetros de comandos.

    Attributes:
        overwrite: Política ante conflicto de salida ya existente.
    """

    overwrite: OverwriteMode


@dataclass(kw_only=True)
class GifParameters(
    BaseParameters,
    InputSingleMixin,
    OutputSingleMixin,
    FpsGifMixin,
    CropMixin,
    ScaleMixin,
    FlipMixin,
    RotateMixin,
    TimestampStartEndMixin,
):
    """Parámetros utilizados por el comando GIF."""


@dataclass(kw_only=True)
class InfoParameters(
    InputSingleMixin,
):
    """Parámetros utilizados por el comando Info."""


@dataclass(kw_only=True)
class SheetParameters(
    BaseParameters,
    InputSingleMixin,
    OutputBatchMixin,
    ImageQualityMixin,
    SheetPresetsMixin,
):
    """Parámetros utilizados por el comando Sheet."""


@dataclass(kw_only=True)
class ThumbnailParameters(
    BaseParameters,
    InputSingleMixin,
    OutputSingleMixin,
    ImageQualityMixin,
    TimestampAtMixin,
    TimestampStartEndMixin,
    SceneMixin,
    FpsImageMixin,
    CropMixin,
    ScaleMixin,
    FlipMixin,
    RotateMixin,
):
    """Parámetros validados y parseados para generar thumbnails."""
