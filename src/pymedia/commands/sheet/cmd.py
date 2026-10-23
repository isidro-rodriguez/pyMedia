"""Comando ``sheet``: compositor de comandos ffmpeg."""

import math
from datetime import timedelta
from fractions import Fraction
from pathlib import Path

from pymedia.commands.sheet.parameters import SheetParameters
from pymedia.errors import (
    MissingParameterError,
    MissingPropertyError,
)
from pymedia.locale_manager import locale_manager
from pymedia.locales import translate as _
from pymedia.models.media import Audio, Media, Subtitles, Video
from pymedia.models.sheet_preset import PresetSheet
from pymedia.utils import parse_quantity, parse_size, parse_timedelta, to_ffmpeg_value


class SheetCmd:
    """Compone los comandos ffmpeg necesarios para generar una hoja de contactos."""

    def __init__(self, params: SheetParameters, tile_tmp: Path) -> None:
        """Inicializa el generador con los parámetros y la ruta temporal intermedia.

        Args:
            params: Parámetros validados y parseados obtenidos de los argumentos
                de CLI.
            tile_tmp: Ruta del fichero temporal intermedio (cuadrícula sin
                cabecera).
        """
        self.params = params
        self.tile_tmp = tile_tmp

    def create_snapshots(self) -> list[str]:
        """Comando ffmpeg para generar una hoja de capturas encadenadas.

        Returns:
            list[str]: Comando ffmpeg para generar cuadrícula de capturas.

        Raises:
            CommandGenerationError: Cuando ocurre un problema en generación de
                comandos.
            MissingParameterError: Si falta algún parámetro requerido (preset,
                media_input, output, pista de audio o subtítulo).
            MissingPropertyError: Si falta alguna propiedad técnica requerida
                en el objeto media (duration, fps, size, video, codec, etc.).
        """
        return self._generate_snapshots()

    def create_header(self) -> list[str]:
        """Comando ffmpeg para añadir cabecera con metadatos a la hoja de capturas.

        Returns:
            list[str]: Comando ffmpeg para añadir cabecera con metadatos.

        Raises:
            CommandGenerationError: Cuando ocurre un problema en generación de
                comandos.
            MissingParameterError: Si falta algún parámetro requerido (preset,
                media_input, output, pista de audio o subtítulo).
            MissingPropertyError: Si falta alguna propiedad técnica requerida
                en el objeto media (duration, fps, size, video, codec, etc.).
        """
        return self._generate_header()

    @property
    def capture_count(self) -> int:
        """Número total de miniaturas (capturas) que compondrán la cuadrícula.

        Returns:
            El resultado de `columns * rows` del preset de hoja activo.

        Raises:
            MissingParameterError: Si no hay un preset de hoja definido.
        """
        preset = self.params.preset_sheet
        if preset is None:
            raise MissingParameterError(name="preset")
        return preset.columns * preset.rows

    def _generate_snapshots(self) -> list[str]:
        """Comando para capturar frames y componer la cuadrícula de miniaturas."""
        params = self.params
        preset = params.preset_sheet
        media = params.media

        if preset is None:
            raise MissingParameterError(name="preset")
        if media is None:
            raise MissingParameterError(name="media")
        if media.duration is None:
            raise MissingPropertyError(name="duration")
        if media.video is None or media.video.format.fps is None:
            raise MissingPropertyError(name="fps")

        fps = media.video.format.fps
        total_frames = int(media.duration.total_seconds() * fps)
        frames = _capture_frames(total_frames, n_captures=preset.columns * preset.rows)
        image_quality = params.to_image_quality_cmd()

        filter_complex = [
            f"split={len(frames)}" + "".join(f"[s{i}]" for i in range(len(frames))),
            *(
                _thumb_filter(i, frame_n, fps, preset, params.thumb_width)
                for i, frame_n in enumerate(frames)
            ),
            _grid_filter(preset, image_format=image_quality.format),
        ]

        return [
            "ffmpeg",
            "-i",
            str(media.path),
            "-filter_complex",
            ";".join(filter_complex),
            "-map",
            "[out]",
            "-frames:v",
            "1",
            *image_quality.compression,
            str(self.tile_tmp),
        ]

    def _generate_header(self) -> list[str]:
        """Genera el comando FFmpeg que superpone la cabecera con metadatos.

        Construye la cabecera de forma resiliente a propiedades ausentes del medio.
        """
        params = self.params
        preset = params.preset_sheet
        media = params.media

        if media is None:
            raise MissingParameterError(name="media")
        if params.image_output is None:
            raise MissingParameterError(name="image_output")
        if preset is None:
            raise MissingParameterError(name="preset")

        video = media.video
        if video is None or video.format.width is None or video.format.height is None:
            raise MissingPropertyError(name="width/height")

        lines = _header_lines(media, video, max_len=preset.max_line_length)
        image_quality = params.to_image_quality_cmd()

        return [
            "ffmpeg",
            "-i",
            str(self.tile_tmp),
            "-vf",
            ",".join(_header_filters(lines, preset, image_format=image_quality.format)),
            *image_quality.compression,
            str(params.image_output),
        ]


# =============================================================================
#  Cuadrícula de miniaturas
# =============================================================================


def _capture_frames(total_frames: int, n_captures: int) -> list[int]:
    """Calcula los índices de los frames que se van a capturar uniformemente."""
    start = int(total_frames * 0.05)
    end = int(total_frames * 0.95)
    step = (end - start) / n_captures
    return [start + int(step * i) for i in range(n_captures)]


def _thumb_filter(
    index: int, frame_n: int, fps: Fraction, preset: PresetSheet, thumb_width: int
) -> str:
    """Construye el filtro que selecciona, rotula y enmarca una miniatura."""
    row, col = divmod(index, preset.columns)
    seconds = timedelta(microseconds=round(frame_n / fps * 1_000_000))
    return (
        f"[s{index}]select='eq(n\\,{frame_n})',showinfo,"
        f"scale={thumb_width}:-1,"
        f"{_timestamp_drawtext(preset, parse_timedelta(seconds))},"
        f"{_thumb_pad(preset)}[{_thumb_label(row, col)}]"
    )


def _thumb_label(row: int, col: int) -> str:
    """Etiqueta de una miniatura; el separador evita colisiones (1,11 vs 11,1)."""
    return f"t{row}_{col}"


def _thumb_pad(preset: PresetSheet) -> str:
    """Construye el filtro pad para bordes y espaciados de cada miniatura."""
    bw = preset.border_width
    half_gap = preset.gap // 2
    border = f"pad=iw+{bw * 2}:ih+{bw * 2}:{bw}:{bw}:color={preset.border_color}"
    gap = (
        f"pad=iw+{half_gap * 2}:ih+{half_gap * 2}:{half_gap}:{half_gap}:"
        f"color={preset.background}"
    )
    return f"{border},{gap}"


def _timestamp_drawtext(preset: PresetSheet, timestamp: str) -> str:
    """Construye el filtro drawtext con la marca de tiempo de la miniatura."""
    ts_margin = 4
    return (
        f"drawtext=fontfile={to_ffmpeg_value(preset.fontfile)}:"
        f"text={to_ffmpeg_value(timestamp)}:expansion=none:"
        f"fontsize={preset.timestamp_fontsize}:"
        f"fontcolor={preset.timestamp_color}:"
        f"bordercolor={preset.timestamp_border_color}:"
        f"borderw={preset.timestamp_border_width}:"
        f"x=w-tw-{ts_margin}:y=h-th-{ts_margin}"
    )


def _grid_filter(preset: PresetSheet, image_format: str) -> str:
    """Apila las miniaturas en la cuadrícula y añade el margen exterior."""
    rows_expr: list[str] = []
    for row in range(preset.rows):
        inputs = "".join(f"[{_thumb_label(row, col)}]" for col in range(preset.columns))
        rows_expr.append(f"{inputs}hstack=inputs={preset.columns}[row{row}]")
    row_labels = "".join(f"[row{row}]" for row in range(preset.rows))
    rows_expr.append(f"{row_labels}vstack=inputs={preset.rows}[grid]")

    m = preset.margin
    return (
        f"{';'.join(rows_expr)},"
        f"[grid]pad=iw+{m * 2}:ih+{m * 2}:{m}:{m}:color={preset.background}, "
        f"{image_format}[out]"
    )


# =============================================================================
#  Cabecera de metadatos
# =============================================================================


def _header_lines(media: Media, video: Video, max_len: int) -> list[str]:
    """Líneas de texto de la cabecera, omitiendo las propiedades ausentes."""
    lines = [f"{_('File')}: {media.path.name}"]
    if size_duration := _size_duration_line(media):
        lines.append(size_duration)
    lines.append(f"{_('Video')}: {_video_details(video, media.video_bit_rate)}")
    if media.audio:
        lines.append(_audio_line(media.audio, max_len))
    if media.subtitles:
        lines.append(_subtitles_line(media.subtitles, max_len))
    return lines


def _header_filters(
    lines: list[str], preset: PresetSheet, image_format: str
) -> list[str]:
    """Filtros que amplían el lienzo y escriben cada línea de la cabecera."""
    line_height = preset.fontsize + preset.line_gap
    header_height = preset.header_margin_top + line_height * len(lines)
    fontfile = to_ffmpeg_value(preset.fontfile)

    filters = [f"pad=iw:ih+{header_height}:0:{header_height}:color={preset.background}"]
    for i, line in enumerate(lines):
        y = preset.header_margin_top + i * line_height
        filters.append(
            f"drawtext=fontfile={fontfile}:"
            f"text={to_ffmpeg_value(line)}:expansion=none:"
            f"fontsize={preset.fontsize}:fontcolor={preset.text_color}:"
            f"x={preset.header_margin_left}:y={y}"
        )
    filters.append(image_format)
    return filters


def _size_duration_line(media: Media) -> str | None:
    """Línea con tamaño y duración del contenedor, si se conoce alguno."""
    locale = locale_manager.detect_language()
    parts: list[str] = []
    if media.format.size:
        size = parse_size(size_bytes=media.format.size, locale=locale)
        parts.append(f"{_('Size')}: {size}")
    if media.duration:
        parts.append(f"{_('Duration')}: {parse_timedelta(media.duration)}")
    return " | ".join(parts) or None


def _video_details(video: Video, bit_rate: float | None) -> str:
    """Resolución, códec, formato de píxel, fps y tasa de bits disponibles."""
    fmt = video.format
    parts = [f"{fmt.width}x{fmt.height}"]
    if fmt.codec:
        parts.append(f"{fmt.codec} ({fmt.profile})" if fmt.profile else fmt.codec)
    if fmt.pix_fmt:
        parts.append(fmt.pix_fmt)
    if fmt.fps:
        parts.append(f"{fmt.fps} fps")
    if bit_rate:
        kbps = parse_quantity(
            value=math.floor(bit_rate / 1000), locale=locale_manager.detect_language()
        )
        parts.append(f"{kbps} kb/s")
    return ", ".join(parts)


def _audio_line(tracks: list[Audio], max_len: int) -> str:
    """Formatea el texto que muestra las pistas de audio del vídeo."""
    items = [
        f"{t.metadata.language or 'und'} "
        f"({t.format.codec or 'audio'} {_format_channels(t.format.channels)})"
        for t in tracks
    ]
    return _truncate_list_display(f"Audio: {len(tracks)} tracks", items, max_len)


def _format_channels(channels: int | None) -> str:
    """Formatea los canales de audio."""
    if channels is None:
        return "unk"
    mapping = {1: "mono", 2: "stereo", 6: "5.1", 8: "7.1"}
    return mapping.get(channels, f"{channels}ch")


def _subtitles_line(subtitles: list[Subtitles], max_len: int) -> str:
    """Construye línea informativa de las pistas de subtítulos en cabecera."""
    # 'und' (undefined) si el idioma no está definido.
    langs = [sub.metadata.language or "und" for sub in subtitles]
    return _truncate_list_display(f"Subtitles: {len(subtitles)} tracks", langs, max_len)


def _truncate_list_display(prefix: str, items: list[str], max_len: int) -> str:
    """Recorta la cabecera con elipsis si excede la longitud del preset."""
    base_template = f"{prefix} [{', '.join(items)}]"
    if len(base_template) <= max_len:
        return base_template
    acc: list[str] = []
    for item in items:
        candidate = f"{prefix} [{', '.join([*acc, item])}, ...]"
        if len(candidate) > max_len:
            break
        acc.append(item)
    if not acc:
        return f"{prefix} [...]"
    return f"{prefix} [{', '.join(acc)}, ...]"
