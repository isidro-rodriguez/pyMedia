from dataclasses import dataclass
from pathlib import Path

from pymedia.errors import MissingParameterError
from pymedia.models.enums import PresetsSheetMode
from pymedia.models.sheet_preset import SheetPreset

_PRESETS: dict[str, SheetPreset] = {
    "fhd": SheetPreset(
        canvas_width=1920,
        columns=5,
        rows=4,
        gap=7,
        line_gap=8,
        margin=10,
        header_margin_top=20,
        header_margin_left=21,
        background="0xffffff",
        border_color="0x222222",
        border_width=2,
        max_line_length=120,
        fontsize=22,
        fontfile=Path("SourceCodePro-Bold.ttf"),
        text_color="0x222222",
        timestamp_fontsize=15,
        timestamp_color="white",
        timestamp_border_width=2,
        timestamp_border_color="0x222222",
    ),
    "hd": SheetPreset(
        canvas_width=1280,
        columns=4,
        rows=3,
        gap=6,
        line_gap=6,
        margin=4,
        header_margin_top=12,
        header_margin_left=14,
        background="0xffffff",
        border_color="0x222222",
        border_width=2,
        max_line_length=80,
        fontfile=Path("SourceCodePro-Bold.ttf"),
        fontsize=14,
        text_color="0x222222",
        timestamp_fontsize=12,
        timestamp_color="white",
        timestamp_border_width=1,
        timestamp_border_color="0x222222",
    ),
    "web": SheetPreset(
        canvas_width=800,
        columns=3,
        rows=3,
        gap=4,
        line_gap=4,
        margin=4,
        header_margin_top=8,
        header_margin_left=11,
        background="0xffffff",
        border_color="0x222222",
        border_width=2,
        max_line_length=50,
        fontfile=Path("SourceCodePro-Bold.ttf"),
        fontsize=12,
        text_color="0x222222",
        timestamp_fontsize=11,
        timestamp_color="white",
        timestamp_border_color="0x222222",
        timestamp_border_width=1,
    ),
}


@dataclass(kw_only=True)
class SheetPresetsMixin:
    """Establece el estilo preajustado indicado por el usuario.

    Parameters:
        preset: Estilo de hoja preajustado.
    """

    preset: SheetPreset | None = None

    def create_sheet_presets(self, preset: PresetsSheetMode) -> None:
        """Carga el estilo de hoja preajustado.

        Args:
            preset: Elección del estilo de hoja preajustado.
        """
        self.preset = _PRESETS[preset.value]

    @property
    def thumb_width(self) -> int:
        """Calcula el ancho dinámico de la captura respetando el canvas total."""
        preset = self.preset

        if preset is None:
            raise MissingParameterError(name="preset")

        total_gaps = (preset.columns - 1) * preset.gap
        total_margins = 2 * preset.margin
        total_borders = 2 * preset.border_width * preset.columns
        available_width = (
            preset.canvas_width - total_margins - total_gaps - total_borders
        )
        return available_width // preset.columns
