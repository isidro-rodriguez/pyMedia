import dataclasses
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import platformdirs

from pymedia.data.types import PresetsSheetMode
from pymedia.errors import MissingParameterError
from pymedia.models.sheet_preset import PresetSheet

_FONT_FILENAME = "SourceCodePro-Bold.ttf"

_PRESETS: dict[str, PresetSheet] = {
    "fhd": PresetSheet(
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
        max_line_length=140,
        fontsize=22,
        fontfile=Path(_FONT_FILENAME),
        text_color="0x222222",
        timestamp_fontsize=15,
        timestamp_color="white",
        timestamp_border_width=2,
        timestamp_border_color="0x222222",
    ),
    "hd": PresetSheet(
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
        max_line_length=120,
        fontfile=Path(_FONT_FILENAME),
        fontsize=14,
        text_color="0x222222",
        timestamp_fontsize=12,
        timestamp_color="white",
        timestamp_border_width=1,
        timestamp_border_color="0x222222",
    ),
    "web": PresetSheet(
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
        max_line_length=100,
        fontfile=Path(_FONT_FILENAME),
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
        preset_sheet: Estilo de hoja preajustado.
    """

    preset_sheet: PresetSheet | None = None

    def create_preset_sheet(self, preset: PresetsSheetMode) -> None:
        """Carga el estilo de hoja preajustado con la fuente instalada.

        Args:
            preset: Elección del estilo de hoja preajustado.
        """
        base = _PRESETS[preset.value]
        font_path = self._resolve_font_asset()
        self.preset_sheet = dataclasses.replace(base, fontfile=font_path)

    @property
    def thumb_width(self) -> int:
        """Calcula el ancho dinámico de la captura respetando el canvas total."""
        preset = self.preset_sheet

        if preset is None:
            raise MissingParameterError(name="preset_sheet")

        total_gaps = (preset.columns - 1) * preset.gap
        total_margins = 2 * preset.margin
        total_borders = 2 * preset.border_width * preset.columns
        available_width = (
            preset.canvas_width - total_margins - total_gaps - total_borders
        )
        return available_width // preset.columns

    @staticmethod
    def _resolve_font_asset() -> Path:
        """Devuelve la ruta de la fuente en el directorio de la app, instalándola si
        falta.
        """
        assets_dir = (
            Path(
                platformdirs.user_config_dir(
                    appname="pymedia", appauthor=False, roaming=True
                )
            )
            / "assets"
        )
        font_path = assets_dir / _FONT_FILENAME

        if not font_path.exists():
            assets_dir.mkdir(parents=True, exist_ok=True)
            data = files("pymedia.resources").joinpath(_FONT_FILENAME).read_bytes()
            font_path.write_bytes(data)

        return font_path
