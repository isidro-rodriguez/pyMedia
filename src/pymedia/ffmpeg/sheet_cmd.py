from datetime import timedelta
from fractions import Fraction
from pathlib import Path

from pymedia import locales
from pymedia.errors import (
    CommandGenerationError,
    MissingMediaError,
    MissingMediaPropertyError,
    MissingParameterError,
)
from pymedia.models.media import Audio, Subtitle
from pymedia.models.pipeline.sheet_pipeline import SheetParameters
from pymedia.services.locale_service import detect_language
from pymedia.utils import parse_quantity, to_ffmpeg_path

# =============================================================================
# Funciones auxiliares
# =============================================================================


def _escape_drawtext(text: str) -> str:
    """Escapa caracteres especiales para el filtro drawtext de FFmpeg."""
    text = text.replace("\\", "\\\\")
    text = text.replace(":", "\\:")
    text = text.replace("%", "\\%")
    text = text.replace("'", r"'\''")
    return text


def _build_duration_display(time: timedelta) -> str:
    """Formatea un objeto timedelta a una cadena con formato HH:MM:SS o MM:SS."""
    total = int(time.total_seconds())
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


# =============================================================================
# Generar cuadrícula de capturas
# =============================================================================


def _generate_snapshots(params: SheetParameters, output: Path) -> list[str]:
    """Genera el comando para capturar frames y componer la cuadrícula de miniaturas."""

    def _calculate_capture_frames() -> list[int]:
        """Calcula los índices de los frames que se van a capturar uniformemente."""
        start = int(total_frames * 0.05)
        end = int(total_frames * 0.95)
        step = (end - start) / n_captures
        return [start + int(step * i) for i in range(n_captures)]

    def _build_thumb_pad() -> str:
        """Construye el filtro pad de para bordes y espaciados de cada miniatura."""
        if preset is None:
            raise MissingParameterError(name="preset")
        bw = preset.border_width
        half_gap = preset.gap // 2
        border = f"pad=iw+{bw * 2}:ih+{bw * 2}:{bw}:{bw}:color={preset.border_color}"
        gap = (
            f"pad=iw+{half_gap * 2}:ih+{half_gap * 2}:{half_gap}:{half_gap}:"
            f"color={preset.background}"
        )
        return f"{border},{gap}"

    def _build_timestamp_drawtext() -> str:
        """Construye el filtro drawtext para superponer la marca de tiempo en la
        miniatura.
        """
        if preset is None:
            raise MissingParameterError(name="preset")
        ts_margin = 4
        return (
            f"drawtext=fontfile='{to_ffmpeg_path(preset.fontfile)}':"
            f"text='{_escape_drawtext(timestamp_str)}':"
            f"fontsize={preset.timestamp_fontsize}:"
            f"fontcolor={preset.timestamp_color}:"
            f"bordercolor={preset.timestamp_border_color}:"
            f"borderw={preset.timestamp_border_width}:"
            f"x=w-tw-{ts_margin}:y=h-th-{ts_margin}"
        )

    def _build_stack_filter() -> str:
        """Construye filtros hstack y vstack para apilar miniaturas en la cuadrícula."""
        if preset is None:
            raise MissingParameterError(name="preset")
        rows_expr = []
        for row in range(preset.rows):
            inputs = "".join(f"[t{row}{col}]" for col in range(preset.columns))
            rows_expr.append(f"{inputs}hstack=inputs={preset.columns}[row{row}]")
        row_labels = "".join(f"[row{row}]" for row in range(preset.rows))
        rows_expr.append(f"{row_labels}vstack=inputs={preset.rows}[grid]")
        return ";".join(rows_expr)

    preset = params.preset_sheet
    media = params.media

    if preset is None:
        raise MissingParameterError(name="preset")
    if params.input_single is None:
        raise MissingParameterError(name="input_single")
    if media is None:
        raise MissingMediaError(path=str(params.input_single))
    if media.duration is None:
        raise MissingMediaPropertyError(name="duration")
    if media.video is None or media.video.fps is None:
        raise MissingMediaPropertyError(name="fps")

    total_frames = int(media.duration.total_seconds() * media.video.fps)
    n_captures = preset.columns * preset.rows
    frames = _calculate_capture_frames()

    split_labels = "".join(f"[s{i}]" for i in range(n_captures))
    filter_complex_parts = [f"split={n_captures}{split_labels}"]

    for i, frame_n in enumerate(frames):
        r, c = divmod(i, preset.columns)
        seconds = timedelta(
            microseconds=round((Fraction(frame_n) / media.video.fps) * 1_000_000)
        )
        timestamp_str = _build_duration_display(seconds)

        filter_complex_parts.append(
            f"[s{i}]select='eq(n\\,{frame_n})',"
            f"scale={params.thumb_width}:-1,"
            f"{_build_timestamp_drawtext()},"
            f"{_build_thumb_pad()}[t{r}{c}]"
        )

    filter_complex_parts.append(_build_stack_filter())

    m = preset.margin
    filter_complex_parts.append(
        f"[grid]pad=iw+{m * 2}:ih+{m * 2}:{m}:{m}:color={preset.background}[out]"
    )

    return [
        "ffmpeg",
        "-y",
        "-i",
        str(params.input_single),
        "-filter_complex",
        ";".join(filter_complex_parts),
        "-map",
        "[out]",
        "-frames:v",
        "1",
        str(output),
    ]


# =============================================================================
# Generar cabecera con metadatos
# =============================================================================


def _generate_header(params: SheetParameters, image_input: Path) -> list[str]:
    """Genera el comando FFmpeg para superponer la cabecera con metadatos sobre la
    cuadrícula.
    """

    def _truncate_list_display(prefix: str, items: list[str], max_len: int) -> str:
        """Trunca la lista agregando puntos suspensivos si supera el ancho máximo."""
        base_template = f"{prefix} [{', '.join(items)}]"
        if len(base_template) <= max_len:
            return base_template
        acc = []
        for item in items:
            candidate = f"{prefix} [{', '.join(acc + [item])}, ...]"
            if len(candidate) > max_len:
                break
            acc.append(item)
        if not acc:
            return f"{prefix} [...]"
        return f"{prefix} [{', '.join(acc)}, ...]"

    def _build_size_display(size_bytes: int) -> str:
        """Formatea el tamaño del archivo en unidades legibles (GB/MB) e incluye el
        total en bytes.
        """
        lang = detect_language()
        size_gb = parse_quantity(value=size_bytes / 1024**3, lang=lang)
        size_mb = parse_quantity(value=size_bytes / 1024**2, lang=lang)
        size_bt = parse_quantity(value=size_bytes, lang=lang)
        if size_bytes > 1024**3:
            return f"{size_gb} GB ({size_bt} bytes)"
        return f"{size_mb} MB ({size_bt} bytes)"

    def _build_audio_line(tracks: list[Audio], max_len: int) -> str | None:
        """Construye la línea informativa de las pistas de audio para la cabecera."""

        def _format_channels(channels: int) -> str:
            """Convierte el número de canales a su denominación estándar."""
            mapping = {1: "mono", 2: "stereo", 6: "5.1", 8: "7.1"}
            return mapping.get(channels, f"{channels}ch")

        if not tracks:
            return None
        formatted_items = []
        for t in tracks:
            if t.channels is None:
                raise MissingParameterError(name="track channels")
            if t.language is None:
                raise MissingParameterError(name="track language")
            if t.codec is None:
                raise MissingParameterError(name="track codec")
            ch_str = _format_channels(t.channels)
            formatted_items.append(f"{t.language} ({t.codec} {ch_str})")
        prefix = f"Audio: {len(tracks)} tracks"
        return _truncate_list_display(prefix, formatted_items, max_len)

    def _build_subtitles_line(subtitles: list[Subtitle], max_len: int) -> str | None:
        """Construye línea informativa de las pistas de subtítulos para la cabecera."""
        if not subtitles:
            return None
        subs: list[str] = []
        for sub in subtitles:
            if sub.language is None:
                raise MissingParameterError(name="subtitle language")
            subs.append(sub.language)
        prefix = f"Subtitles: {len(subtitles)} tracks"
        return _truncate_list_display(prefix, subs, max_len)

    preset = params.preset_sheet
    media = params.media
    if params.input_single is None:
        raise MissingParameterError(name="input_single")
    if media is None:
        raise MissingMediaError(path=str(params.input_single))
    video = media.video
    if params.output is None:
        raise MissingParameterError(name="output")
    if preset is None:
        raise MissingParameterError(name="preset")
    if media.size is None:
        raise MissingMediaPropertyError(name="size")
    if media.duration is None:
        raise MissingMediaPropertyError(name="duration")
    if video is None:
        raise MissingMediaPropertyError(name="video")
    if video.width is None:
        raise MissingMediaPropertyError(name="video width")
    if video.height is None:
        raise MissingMediaPropertyError(name="video height")
    if video.codec is None:
        raise MissingMediaPropertyError(name="video codec")
    if video.profile is None:
        raise MissingMediaPropertyError(name="video profile")
    if video.pix_fmt is None:
        raise MissingMediaPropertyError(name="video pix_fmt")
    if video.fps is None:
        raise MissingMediaPropertyError(name="video fps")
    if video.bit_rate is None:
        raise MissingMediaPropertyError(name="video bit_rate")

    bit_rate = parse_quantity(value=video.bit_rate, lang=detect_language())

    lines = [
        f"{locales.Sheet['file']}: {params.input_single.name}",
        f"{locales.Sheet['size']}: {_build_size_display(media.size)} | "
        f"{locales.Sheet['duration']}: {_build_duration_display(media.duration)}",
        f"{locales.Sheet['video']}: {video.width}x{video.height}, {video.codec} "
        f"({video.profile}), {video.pix_fmt}, {video.fps} fps, {bit_rate} kb/s",
    ]

    if media.audio is not None:
        audio_line = _build_audio_line(
            tracks=media.audio, max_len=preset.max_line_length
        )
        if audio_line:
            lines.append(audio_line)

    if media.subtitles is not None:
        sub_line = _build_subtitles_line(
            subtitles=media.subtitles, max_len=preset.max_line_length
        )
        if sub_line:
            lines.append(sub_line)

    line_height = preset.fontsize + preset.line_gap
    header_height = preset.header_margin_top + line_height * len(lines)

    filters = [f"pad=iw:ih+{header_height}:0:{header_height}:color={preset.background}"]
    for i, line in enumerate(lines):
        y = preset.header_margin_top + i * line_height
        filters.append(
            f"drawtext=fontfile='{to_ffmpeg_path(preset.fontfile)}':"
            f"text='{_escape_drawtext(line)}':"
            f"fontsize={preset.fontsize}:fontcolor={preset.text_color}:"
            f"x={preset.header_margin_left}:y={y}"
        )

    return [
        "ffmpeg",
        "-y",
        "-i",
        str(image_input),
        "-vf",
        ",".join(filters),
        str(params.output),
    ]


# =============================================================================
# Proceso
# =============================================================================


def sheet_cmd(params: SheetParameters, tile_tmp: Path) -> list[list[str]]:
    """Composición de llamada ffmpeg para generar una hoja de captura encadenada.

    Args:
        params: Parámetros validados y parseados obtenidos de los argumentos de CLI.
        tile_tmp: Ruta del fichero temporal intermedio (cuadrícula sin cabecera).

    Returns:
        list[list[str]]: Lista de comandos ffmpeg listos para su ejecución secuencial.

    Raises:
        CommandGenerationError: Si ocurre un problema en la generación de los comandos.
        MissingParameterError: Si falta algún parámetro requerido (preset,
            input_single, output, pista de audio o subtítulo).
        MissingMediaError: Si el objeto de metadatos del medio es None.
        MissingMediaPropertyError: Si falta alguna propiedad técnica requerida en el
            objeto media (duration, fps, size, video, codec, etc.).
    """

    snapshots_cmd = _generate_snapshots(params=params, output=tile_tmp)

    if snapshots_cmd is None:
        raise CommandGenerationError(command_name="snapshots_cmd")

    header_cmd = _generate_header(params=params, image_input=tile_tmp)

    if header_cmd is None:
        raise CommandGenerationError(command_name="header_cmd")

    return [snapshots_cmd, header_cmd]
