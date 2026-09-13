"""Generación de comandos ffmpeg para la hoja de contactos (sheet)."""

from datetime import timedelta
from fractions import Fraction
from pathlib import Path

from pymedia.errors import (
    CommandGenerationError,
    MissingParameterError,
    MissingPropertyError,
)
from pymedia.locale_manager import locale_manager
from pymedia.locales import _  # noqa
from pymedia.models.media import Audio, Subtitles
from pymedia.models.parameters import SheetParameters
from pymedia.utils import parse_quantity, parse_size, parse_timedelta, to_ffmpeg_path


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
        snapshots_cmd = self._generate_snapshots()
        if snapshots_cmd is None:
            raise CommandGenerationError(name="snapshots_cmd")

        return snapshots_cmd

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
        header_cmd = self._generate_header()
        if header_cmd is None:
            raise CommandGenerationError(name="header_cmd")

        return header_cmd

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

    @staticmethod
    def _escape_drawtext(text: str) -> str:
        """Escapa caracteres especiales para el filtro drawtext de FFmpeg."""
        text = text.replace("\\", "\\\\")
        text = text.replace(":", "\\:")
        text = text.replace("%", "\\%")
        text = text.replace("'", r"'\''")
        return text

    def _generate_snapshots(self) -> list[str]:
        """Comando para capturar frames y componer la cuadrícula de miniaturas."""

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
            border = (
                f"pad=iw+{bw * 2}:ih+{bw * 2}:{bw}:{bw}:color={preset.border_color}"
            )
            gap = (
                f"pad=iw+{half_gap * 2}:ih+{half_gap * 2}:{half_gap}:{half_gap}:"
                f"color={preset.background}"
            )
            return f"{border},{gap}"

        def _build_timestamp_drawtext() -> str:
            """Construye el filtro drawtext con la marca de tiempo de la miniatura."""
            if preset is None:
                raise MissingParameterError(name="preset")
            ts_margin = 4
            return (
                f"drawtext=fontfile='{to_ffmpeg_path(preset.fontfile)}':"
                f"text='{self._escape_drawtext(timestamp_str)}':"
                f"fontsize={preset.timestamp_fontsize}:"
                f"fontcolor={preset.timestamp_color}:"
                f"bordercolor={preset.timestamp_border_color}:"
                f"borderw={preset.timestamp_border_width}:"
                f"x=w-tw-{ts_margin}:y=h-th-{ts_margin}"
            )

        def _build_stack_filter() -> str:
            """Construye filtros hstack y vstack para miniaturas en la cuadrícula."""
            if preset is None:
                raise MissingParameterError(name="preset")
            rows_expr = []
            for row in range(preset.rows):
                inputs = "".join(f"[t{row}{col}]" for col in range(preset.columns))
                rows_expr.append(f"{inputs}hstack=inputs={preset.columns}[row{row}]")
            row_labels = "".join(f"[row{row}]" for row in range(preset.rows))
            rows_expr.append(f"{row_labels}vstack=inputs={preset.rows}[grid]")
            return ";".join(rows_expr)

        params = self.params
        output = self.tile_tmp
        preset = params.preset_sheet
        media = params.media

        if preset is None:
            raise MissingParameterError(name="preset")
        if media is None:
            raise MissingParameterError(name="media")
        if media.duration is None:
            raise MissingPropertyError(name="duration")
        if media.video is None or media.video.fps is None:
            raise MissingPropertyError(name="fps")

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
            timestamp_str = parse_timedelta(seconds)

            filter_complex_parts.append(
                f"[s{i}]select='eq(n\\,{frame_n})',showinfo,"
                f"scale={params.thumb_width}:-1,"
                f"{_build_timestamp_drawtext()},"
                f"{_build_thumb_pad()}[t{r}{c}]"
            )

        m = preset.margin
        filter_complex_parts.append(
            f"{_build_stack_filter()},"
            f"[grid]pad=iw+{m * 2}:ih+{m * 2}:{m}:{m}:color={preset.background}, "
            f"{params.to_image_quality_cmd().format}[out]"
        )

        return [
            "ffmpeg",
            "-y",
            "-i",
            str(media.path),
            "-filter_complex",
            ";".join(filter_complex_parts),
            "-map",
            "[out]",
            "-frames:v",
            "1",
            *params.to_image_quality_cmd().compression,
            "-progress",
            "pipe:1",
            "-nostats",
            str(output),
        ]

    def _generate_header(self) -> list[str]:
        """Genera el comando FFmpeg que superpone la cabecera con metadatos.

        Construye la cabecera de forma resiliente a propiedades ausentes del medio.
        """

        def _truncate_list_display(prefix: str, items: list[str], max_len: int) -> str:
            """Recorta la cabecera con elipsis si excede la longitud del preset."""
            base_template = f"{prefix} [{', '.join(items)}]"
            if len(base_template) <= max_len:
                return base_template
            acc: list[str] = []
            for item in items:
                candidate = f"{prefix} [{', '.join(acc + [item])}, ...]"
                if len(candidate) > max_len:
                    break
                acc.append(item)
            if not acc:
                return f"{prefix} [...]"
            return f"{prefix} [{', '.join(acc)}, ...]"

        def _build_audio_line(tracks: list[Audio], max_len: int) -> str | None:
            """Formatea el texto que muestra las pistas de audio del vídeo."""

            def _format_channels(channels: int | None) -> str:
                """Formatea los canales de audio."""
                if channels is None:
                    return "unk"
                mapping = {1: "mono", 2: "stereo", 6: "5.1", 8: "7.1"}
                return mapping.get(channels, f"{channels}ch")

            if not tracks:
                return None
            formatted_items = []
            for t in tracks:
                lang_str = t.language or "und"
                codec_str = t.codec or "audio"
                ch_str = _format_channels(t.channels)
                formatted_items.append(f"{lang_str} ({codec_str} {ch_str})")
            prefix = f"Audio: {len(tracks)} tracks"
            return _truncate_list_display(prefix, formatted_items, max_len)

        def _build_subtitles_line(
            subtitles: list[Subtitles], max_len: int
        ) -> str | None:
            """Construye línea informativa de las pistas de subtítulos en cabecera."""
            if not subtitles:
                return None

            subs: list[str] = []
            for sub in subtitles:
                # Usar 'und' (undefined) si sub.language es None o está vacío
                lang = sub.language if sub.language else "und"
                subs.append(lang)

            prefix = f"Subtitles: {len(subtitles)} tracks"
            return _truncate_list_display(prefix, subs, max_len)

        params = self.params
        image_input = self.tile_tmp
        preset = params.preset_sheet
        media = params.media

        # Validaciones críticas de estructura básica
        if media is None:
            raise MissingParameterError(name="media")
        if params.image_output is None:
            raise MissingParameterError(name="image_output")
        if preset is None:
            raise MissingParameterError(name="preset")

        video = media.video
        if video is None or video.width is None or video.height is None:
            raise MissingPropertyError(name="width/height")

        # Construcción dinámica de detalles de vídeo (manejando opcionales)
        video_parts = [f"{video.width}x{video.height}"]

        if video.codec:
            codec_info = video.codec
            if video.profile:
                codec_info += f" ({video.profile})"
            video_parts.append(codec_info)

        if video.pix_fmt:
            video_parts.append(video.pix_fmt)

        if video.fps:
            video_parts.append(f"{video.fps} fps")

        # Bitrate: Usar el explícito, o calcularlo aproximadamente por tamaño/duración
        bit_rate_val: float | None = video.bit_rate
        if (
            bit_rate_val is None
            and media.size
            and media.duration
            and media.duration.total_seconds() > 0
        ):
            bit_rate_val = (media.size * 8) / (media.duration.total_seconds() * 1000)

        if bit_rate_val:
            bit_rate_str = parse_quantity(
                value=bit_rate_val, locale=locale_manager.detect_language()
            )
            video_parts.append(f"{bit_rate_str} kb/s")

        # Ensamblado de líneas
        lines = [f"{_('File')}: {media.path}"]

        size_dur_parts = []
        if media.size:
            size_dur_parts.append(
                f"{_('Size')}: {
                    parse_size(
                        size_bytes=media.size, locale=locale_manager.detect_language()
                    )
                }"
            )
        if media.duration:
            size_dur_parts.append(f"{_('Duration')}: {parse_timedelta(media.duration)}")
        if size_dur_parts:
            lines.append(" | ".join(size_dur_parts))

        lines.append(f"{_('Video')}: {', '.join(video_parts)}")

        if media.audio and len(media.audio) > 0:
            audio_line = _build_audio_line(
                tracks=media.audio, max_len=preset.max_line_length
            )
            if audio_line:
                lines.append(audio_line)

        if media.subtitles and len(media.subtitles) > 0:
            sub_line = _build_subtitles_line(
                subtitles=media.subtitles, max_len=preset.max_line_length
            )
            if sub_line:
                lines.append(sub_line)

        line_height = preset.fontsize + preset.line_gap
        header_height = preset.header_margin_top + line_height * len(lines)
        fontfile = to_ffmpeg_path(preset.fontfile)
        fontfile_quoted = f'"{fontfile}"' if "'" in fontfile else f"'{fontfile}'"

        filters = [
            f"pad=iw:ih+{header_height}:0:{header_height}:color={preset.background}"
        ]
        for i, line in enumerate(lines):
            y = preset.header_margin_top + i * line_height
            filters.append(
                f"drawtext=fontfile={fontfile_quoted}:"
                f"text='{self._escape_drawtext(line)}':"
                f"fontsize={preset.fontsize}:fontcolor={preset.text_color}:"
                f"x={preset.header_margin_left}:y={y}"
            )
        filters.append(params.to_image_quality_cmd().format)

        return [
            "ffmpeg",
            "-y",
            "-i",
            str(image_input),
            "-vf",
            ",".join(filters),
            *params.to_image_quality_cmd().compression,
            str(params.image_output),
        ]
