from pymedia.models.config import Config
from pymedia.models.media import Media
from pymedia.models.video_pipeline import VideoPipeline
from pymedia.utils import parse_crop


def _target_fps(media_infos: list[Media], mode: str) -> str:
    """Calcula el fps objetivo según el modo min/max del config."""
    fps_values = []
    for media in media_infos:
        if media.video is not None and media.video.fps is not None:
            fps_values.append(media.video.fps)

    if not fps_values:
        return "30"

    if mode == "max":
        target = max(fps_values)
    else:  # min
        target = min(fps_values)

    return str(target)


def _channel_layout(mode: str) -> str:
    """Devuelve el channel_layout según el modo del config."""
    return "stereo" if mode == "stereo" else "mono"


def _target_height(media_infos: list[Media], resize_to: str) -> int:
    """Calcula la altura objetivo según el modo min/max del config."""
    video_heights = []
    for media in media_infos:
        if media.video is None:
            raise ValueError("Stream de vídeo no encontrado en unión recodificada")
        video_heights.append(media.video.height)

    match resize_to:
        case "min_height":
            return min(video_heights)
        case "max_height":
            return max(video_heights)
        case _:
            raise ValueError(f"Valor inválido para resize_to: {resize_to}")


def _needs_scale(media_infos: list[Media], pipeline: VideoPipeline) -> bool:
    """True si hay que escalar: alturas distintas o escala explícita del usuario."""
    heights = {m.video.height for m in media_infos if m.video is not None}

    if heights is None:
        raise ValueError("Alturas de vídeos inválida")

    all_same = len(heights) <= 1

    if all_same:
        # Solo escalar si el usuario pidió una resolución menor
        height = next(iter(heights))
        return pipeline.scale is not None and height > pipeline.scale

    # Alturas diferentes → necesitan escalado para normalizar
    return True


def _needs_fps(media_infos: list[Media]) -> bool:
    """True si los vídeos tienen fps distintos (o desconocido)."""
    return len({m.video.fps for m in media_infos if m.video is not None}) > 1


def _needs_pix_fmt(media_infos: list[Media]) -> bool:
    """True si los vídeos tienen pix_fmt distintos (o desconocido)."""
    return len({m.video.pix_fmt for m in media_infos if m.video is not None}) > 1


def _all_audio_compatible(media_infos: list[Media]) -> bool:
    """True si todos tienen audio y son idénticos en codec/rate/channels/layout."""
    if any(m.audio is None for m in media_infos):
        return False
    signatures = {
        (m.audio.codec, m.audio.sample_rate, m.audio.channels, m.audio.channel_layout)
        for m in media_infos
    }
    return len(signatures) == 1


def _determine_targets(
    media_infos: list[Media], config: Config, pipeline: VideoPipeline
) -> dict:
    """Determina los targets y qué normalización es realmente necesaria."""
    return {
        "height": _target_height(media_infos, config.conflictive_join.resize_to),
        "fps": _target_fps(media_infos, config.conflictive_join.fps),
        "pix_fmt": config.conflictive_join.pix_fmt,
        "channel_layout": _channel_layout(config.conflictive_join.channels),
        "needs_scale": _needs_scale(media_infos, pipeline),
        "needs_fps": _needs_fps(media_infos),
        "needs_pix_fmt": _needs_pix_fmt(media_infos),
        "all_audio_compatible": _all_audio_compatible(media_infos),
        "has_audio": any(m.audio is not None for m in media_infos),
    }


def _build_input_args(media_infos: list[Media]) -> list[str]:
    """Construye los argumentos -i de ffmpeg para todas las entradas."""
    args: list[str] = []
    for media in media_infos:
        args.append("-i")
        args.append(str(media.path.absolute()))
    return args


def _build_video_chain(
    media: Media, index: int, target: dict, pipeline: VideoPipeline
) -> str:
    """Construye la cadena de filtros de vídeo para una entrada."""
    if media.video is None:
        raise ValueError("Stream de vídeo no encontrado en unión recodificada")

    video_filters: list[str] = []

    # Si opción de cortado de imagen
    if pipeline.crop is not None:
        parsed = parse_crop(pipeline.crop)
        if parsed is None:
            raise ValueError("Crop no encontrado en unión recodificada")
        left, right, top, bottom = parsed

        crop_w = media.video.width - left - right
        crop_h = media.video.height - top - bottom
        video_filters.append(f"crop={crop_w}:{crop_h}:{left}:{top}")

    # Si opción giro
    if pipeline.gyrate is not None:
        match pipeline.gyrate:
            case 90:
                video_filters.append("transpose=1")
            case 180:
                video_filters.append("vflip,hflip")
            case 270:
                video_filters.append("transpose=2")

    # Escalado — solo si es necesario
    if target["needs_scale"]:
        if pipeline.scale is not None:
            video_filters.append(f"scale=-2:{pipeline.scale}")
        else:
            video_filters.append(f"scale=-2:{target['height']}")

    video_filter_str = ",".join(video_filters)
    if video_filter_str:
        video_filter_str += ","

    # Normalización común — se omiten filtros no necesarios
    normalization = ["setsar=1"]
    if target["needs_fps"]:
        normalization.append(f"fps={target['fps']}")
    if target["needs_pix_fmt"]:
        normalization.append(f"format={target['pix_fmt']}")
    normalization.append("setpts=PTS-STARTPTS")

    return f"[{index}:v]{video_filter_str}{','.join(normalization)}[v{index}]"


def _build_audio_chain(media: Media, index: int, target: dict) -> str:
    """Construye la cadena de filtros de audio para una entrada."""
    if media.audio is None:
        raise ValueError("Stream de audio no encontrado en unión recodificada")

    if target["all_audio_compatible"]:
        # Todos los audios son idénticos — solo resetear timestamps
        return f"[{index}:a]asetpts=PTS-STARTPTS[a{index}]"

    # Audios incompatibles → normalizar
    # noinspection SpellCheckingInspection
    return (
        f"[{index}:a]aresample=48000,"
        f"aformat=sample_fmts=fltp:channel_layouts={target['channel_layout']},"
        f"asetpts=PTS-STARTPTS[a{index}]"
    )


def _build_concat_graph(n: int, has_audio: bool = True) -> str:
    """Construye el grafo concat final con en entradas."""
    if has_audio:
        labels = "".join(f"[v{i}][a{i}]" for i in range(n))
        return f"{labels}concat=n={n}:v=1:a=1[v][a]"
    labels = "".join(f"[v{i}]" for i in range(n))
    return f"{labels}concat=n={n}:v=1:a=0[v]"


def _build_ffmpeg_command(
    input_args: list[str],
    filters: str,
    config: Config,
    output: str,
    has_audio: bool = True,
) -> list[str]:
    """Ensambla el comando ffmpeg completo."""
    cmd = [
        "ffmpeg",
        "-y",
        "-nostdin",
        "-loglevel",
        "error",
        *input_args,
        "-filter_complex",
        filters,
        "-map",
        "[v]",
        "-c:v",
        config.encode.video_codec,
        "-preset",
        config.encode.video_preset,
        "-crf",
        str(config.encode.video_crf),
        "-threads",
        "1",
    ]
    if has_audio:
        cmd.extend(["-map", "[a]", "-c:a", config.encode.audio_codec])
    cmd.append(output)
    return cmd


def concat_filter_cmd(media_infos: list[Media], pipeline: VideoPipeline, output: str):
    """Construye el comando ffmpeg para unión recodificada con filter_complex."""
    config = Config.load()
    target = _determine_targets(media_infos, config, pipeline)

    input_args = _build_input_args(media_infos)

    media_filters: list[str] = []
    for i, media in enumerate(media_infos):
        media_filters.append(_build_video_chain(media, i, target, pipeline))
        if target["has_audio"]:
            media_filters.append(_build_audio_chain(media, i, target))

    filters = (
        ";".join(media_filters)
        + ";"
        + _build_concat_graph(len(media_infos), target["has_audio"])
    )

    cmd = _build_ffmpeg_command(
        input_args, filters, config, output, has_audio=target["has_audio"]
    )

    return cmd
