from dataclasses import dataclass
from pathlib import Path


@dataclass(kw_only=True, slots=True, frozen=True)
class PresetSheet:
    """Configuración del estilo gráfico usado en las hojas de captura consecutivas.

    Attributes:
        canvas_width: Ancho de la hoja de capturas de vídeo.
        columns: Número de columnas de la hoja.
        rows: Numero de filas de la hoja.
        gap: Distancias entre bordes de capturas de vídeo.
        line_gap: Distancia entre filas de texto.
        margin: Distancia entre los bordes de capturas al marco de la hoja.
        header_margin_top: Distancia del texto de cabecera al marco superior de la hoja.
        header_margin_left: Distancia del texto de cabecera al marco izquierdo.
        background: Color del fondo de la hoja.
        border_color: Color de los bordes de las capturas.
        border_width: Ancho de los bordes de capturas.
        max_line_length: Máximo número de caracteres por línea en la hoja.
        fontfile: Ruta a la tipografía usada.
        fontsize: Tamaño de la fuente.
        text_color: Color de texto.
        timestamp_fontsize: Tamaño de fuente de marcas de tiempo en capturas.
        timestamp_color: Color del texto en las capturas.
        timestamp_border_color: Color del borde del texto en las capturas.
        timestamp_border_width: Ancho del borde de texto en las capturas.
    """

    canvas_width: int
    columns: int
    rows: int
    gap: int
    line_gap: int
    margin: int
    header_margin_top: int
    header_margin_left: int
    background: str
    border_color: str
    border_width: int
    max_line_length: int
    fontfile: Path
    fontsize: int
    text_color: str
    timestamp_fontsize: int
    timestamp_color: str
    timestamp_border_color: str
    timestamp_border_width: int
