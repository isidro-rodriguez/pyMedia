"""Genera los vídeos de prueba a partir de las pistas ya generadas.

Los vídeos incrustan (sin recodificar) las pistas de `audio_tracks` y los
subtítulos de `subtitle_tracks`, que deben existir antes de ejecutar este
módulo. Además de los metadatos por stream, cada vídeo lleva metadatos de
contenedor (title/comment) que describen el propósito de esa fixture.
"""

from dataclasses import dataclass
from itertools import cycle, islice
from pathlib import Path

from ._common import (
    DURATION_SECONDS,
    FIXTURES_DIR,
    FPS,
    RESOLUTION,
    FixtureGenerationError,
    print_generated,
    run_ffmpeg,
)
from .audio_tracks import TRACKS, TrackSpec, track_path
from .subtitle_tracks import SUBTITLES, subtitle_path

H264 = ("-c:v", "libx264", "-pix_fmt", "yuv420p")
FASTSTART = ("-movflags", "+faststart")  # reproducción progresiva del MP4


def _lavfi(source: str, size: str = RESOLUTION) -> str:
    """Fuente de vídeo sintética de lavfi con la duración y los fps comunes."""
    return f"{source}=size={size}:rate={FPS}:duration={DURATION_SECONDS}"


def _mandelbrot(maxiter: int = 200) -> str:
    """Fractal de Mandelbrot con zoom suave y continuo (más maxiter, más CPU)."""
    fractal = f"mandelbrot=size={RESOLUTION}:rate={FPS}:maxiter={maxiter}"
    zoom = (
        "zoompan=z='min(zoom+0.0015,2.5)':"
        "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d=1:s={RESOLUTION}:fps={FPS}"
    )
    return f"{fractal},{zoom},trim=duration={DURATION_SECONDS},setpts=PTS-STARTPTS"


@dataclass(frozen=True, slots=True)
class VideoSpec:
    """Especificación de un vídeo de prueba.

    Attributes:
        filename: Nombre del fichero de salida. Su extensión decide qué pistas
            de audio se incrustan (según `TrackSpec.compatible_with`).
        source: Fuente de vídeo de lavfi.
        video_args: Opciones de codificación de vídeo.
        output_args: Opciones adicionales del muxer.
        subtitle_format: Formato de los subtítulos a incrustar; `None` = ninguno.
        null_metadata: Si es `True`, deja sin title/language/disposition
            todos los streams, y sin metadatos de contenedor (para probar
            vídeos con metadatos ausentes).
        audio_count: Nº de pistas de audio; `None` = todas las compatibles.
            Si supera las disponibles, se reutilizan cíclicamente.
        tags: Pares (language, title) a usar en las pistas de audio en vez de
            los de `TrackSpec`. Su longitud fija el nº de pistas de audio.
        truncate_ratio: Fracción del fichero que se conserva tras generarlo
            (simula una descarga incompleta); `None` = fichero completo.
        container_tags: Pares (clave, valor) de metadatos de contenedor
            (`title`, `comment`, `genre`...). Se ignora si `null_metadata`
            es `True`, ya que `-map_metadata -1` los borra igualmente.
    """

    filename: str
    source: str
    video_args: tuple[str, ...]
    output_args: tuple[str, ...] = ()
    subtitle_format: str | None = None
    null_metadata: bool = False
    audio_count: int | None = None
    tags: tuple[tuple[str, str], ...] = ()
    truncate_ratio: float | None = None
    container_tags: tuple[tuple[str, str], ...] = ()


# Casos límite de idioma y título: emoji, comillas, `=`, salto de línea,
# espacios en los extremos, códigos no estándar, título largo y vacío.
HOSTILE_TAGS: tuple[tuple[str, str], ...] = (
    ("und", "🎵 emoji ñ 日本語"),
    ("es", "comillas \"dobles\" y 'simples'"),
    ("fre", "a=b=c"),
    ("xxx", "línea 1\nlínea 2"),
    ("eng", "  espacios  "),
    ("spa", "x" * 500),
    ("eng", ""),
)

# Todas las claves de metadatos de contenedor que ffmpeg vuelca tal cual en
# los "Tags" de Matroska: usadas en metadata.mkv para probar el contenedor
# con la máxima cobertura de metadatos posible.
METADATA_MKV_TAGS: tuple[tuple[str, str], ...] = (
    ("title", "Metadatos completos"),
    ("comment", "Audio, vídeo y subtítulos ASS con metadatos completos."),
    ("description", "Fixture con el máximo de metadatos de contenedor soportados."),
    ("synopsis", "Vídeo de prueba pensado para validar la lectura de tags MKV."),
    ("genre", "Test"),
    ("date", "2026-09-24"),
    ("copyright", "© pyMedia"),
    ("encoder", "pyMedia fixture generator"),
    ("artist", "pyMedia"),
    ("album", "pyMedia fixtures"),
    ("track", "1"),
    ("law_rating", "N/A"),
)


VIDEOS: tuple[VideoSpec, ...] = (
    VideoSpec(
        filename="simple.mp4",
        source=_mandelbrot(),
        video_args=("-c:v", "libsvtav1", "-crf", "30", "-preset", "8"),
        output_args=("-t", str(DURATION_SECONDS), *FASTSTART),
        container_tags=(
            ("title", "Fractal simple"),
            ("comment", "Vídeo AV1 con fractal de Mandelbrot y zoom continuo."),
        ),
    ),
    VideoSpec(
        filename="portrait.mp4",
        source=_lavfi("testsrc2", size="720x1280"),
        video_args=(*H264, "-crf", "23", "-vf", "setsar=1"),
        output_args=FASTSTART,
        container_tags=(
            ("title", "Vídeo vertical"),
            ("comment", "Formato retrato 720x1280 para pruebas de orientación."),
        ),
    ),
    VideoSpec(
        filename="metadata.mkv",
        source=_lavfi("testsrc"),
        video_args=H264,
        subtitle_format="ass",
        container_tags=METADATA_MKV_TAGS,
    ),
    VideoSpec(
        filename="test_null_metadata.mkv",
        source=_lavfi("testsrc2"),
        video_args=H264,
        subtitle_format="srt",
        null_metadata=True,
    ),
    VideoSpec(
        filename="noaudio.mkv",
        source=_lavfi("testsrc2"),
        video_args=H264,
        audio_count=0,
        container_tags=(
            ("title", "Sin audio"),
            ("comment", "Vídeo sin pistas de audio."),
        ),
    ),
    VideoSpec(
        filename="lots.mkv",
        source=_lavfi("testsrc2"),
        video_args=H264,
        audio_count=32,
        container_tags=(
            ("title", "Muchas pistas de audio"),
            ("comment", "32 pistas de audio reutilizadas cíclicamente."),
        ),
    ),
    VideoSpec(
        filename="hostile.mkv",
        source=_lavfi("testsrc2"),
        video_args=H264,
        tags=HOSTILE_TAGS,
        container_tags=(
            ("title", "Etiquetas hostiles"),
            ("comment", "Idiomas y títulos límite: emoji, comillas, saltos de línea."),
        ),
    ),
    VideoSpec(
        filename="weird ñ [1] 'x'.mkv",
        source=_lavfi("testsrc2"),
        video_args=H264,
        container_tags=(
            ("title", "Nombre de fichero raro"),
            ("comment", "Nombre de fichero con caracteres especiales."),
        ),
    ),
    # Sin `faststart`, el átomo `moov` queda al final y el recorte lo destruye.
    VideoSpec(
        filename="cut.mp4",
        source=_lavfi("testsrc2"),
        video_args=H264,
        truncate_ratio=0.5,
        container_tags=(
            ("title", "Fichero truncado"),
            ("comment", "Recortado al 50% tras generarse: simula descarga incompleta."),
        ),
    ),
)


def select_audio(spec: VideoSpec) -> list[TrackSpec]:
    """Selecciona las pistas de audio válidas para el contenedor del vídeo.

    Args:
        spec: Especificación del vídeo.

    Returns:
        Pistas de `TRACKS` compatibles con la extensión de `spec.filename`,
        repetidas cíclicamente si `spec` pide más (`tags` o `audio_count`).
    """
    suffix = Path(spec.filename).suffix
    compatible = [track for track in TRACKS if suffix in track.compatible_with]
    count = len(spec.tags) if spec.tags else spec.audio_count
    if count is None:
        return compatible
    return list(islice(cycle(compatible), count))


def _subtitle_files(extension: str | None, root: Path) -> list[tuple[str, Path]]:
    """Devuelve pares (idioma, ruta) de los subtítulos a incrustar."""
    if extension is None:
        return []
    return [(lang, subtitle_path(lang, extension, root)) for lang in SUBTITLES]


def _require(paths: list[Path]) -> None:
    """Lanza si falta alguna pista previa (la generan otros módulos)."""
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        msg = f"Faltan fixtures previos, genera antes audio y subtítulos: {missing}"
        raise FixtureGenerationError(msg)


def _map_args(n_audio: int, n_subtitles: int) -> list[str]:
    """Mapea 1 vídeo (input 0) + N audios + N subtítulos, en ese orden."""
    args = ["-map", "0:v:0"]
    for index in range(1, n_audio + 1):
        args += ["-map", f"{index}:a:0"]
    for index in range(n_audio + 1, n_audio + n_subtitles + 1):
        args += ["-map", f"{index}:s:0"]
    return args


def _stream_metadata(kind: str, index: int, **tags: str) -> list[str]:
    """Opciones `-metadata:s` de un stream (un valor vacío borra la etiqueta)."""
    args: list[str] = []
    for key, value in tags.items():
        args += [f"-metadata:s:{kind}:{index}", f"{key}={value}"]
    return args


def _audio_tags(spec: VideoSpec, tracks: list[TrackSpec]) -> list[tuple[str, str]]:
    """Pares (idioma, título) de las pistas de audio: los de `spec` o los propios."""
    return list(spec.tags) or [(track.language, track.title) for track in tracks]


def _container_metadata_args(spec: VideoSpec) -> list[str]:
    """Metadatos de contenedor (`-metadata`) de `spec.container_tags`."""
    args: list[str] = []
    for key, value in spec.container_tags:
        args += ["-metadata", f"{key}={value}"]
    return args


def _metadata_args(
    audio_tags: list[tuple[str, str]], languages: list[str]
) -> list[str]:
    """Metadatos de idioma y título de cada pista de audio y subtítulos."""
    args: list[str] = []
    for i, (language, title) in enumerate(audio_tags):
        args += _stream_metadata("a", i, language=language, title=title)
    for i, language in enumerate(languages):
        args += _stream_metadata("s", i, language=language, title=f"Sub {language}")
    return args


def _null_metadata_args(n_audio: int, n_subtitles: int) -> list[str]:
    """Vacía metadatos y disposition de todos los streams, y los capítulos.

    `-map_metadata -1` ya borra los metadatos de contenedor, por lo que
    `spec.container_tags` no se aplica cuando `null_metadata` es `True`.
    """
    args = ["-map_metadata", "-1", "-map_chapters", "-1"]
    # ffmpeg/libx264 inyectan un tag "encoder" y marcan "default" la primera
    # pista de cada tipo: se vacían para que no quede ningún metadato "vivo".
    for kind, count in (("v", 1), ("a", n_audio), ("s", n_subtitles)):
        for i in range(count):
            args += _stream_metadata(kind, i, title="", language="", encoder="")
            args += [f"-disposition:{kind}:{i}", "0"]
    return args


def build_ffmpeg_args(
    spec: VideoSpec, output: Path, root: Path = FIXTURES_DIR
) -> list[str]:
    """Ensambla los argumentos de ffmpeg: inputs, mapeo, códecs y metadatos.

    Args:
        spec: Especificación del vídeo.
        output: Ruta del fichero de salida.
        root: Directorio raíz de fixtures donde están las pistas.

    Returns:
        Argumentos de ffmpeg (sin el ejecutable).

    Raises:
        FixtureGenerationError: Si faltan pistas de audio o subtítulos.
    """
    tracks = select_audio(spec)
    audio_paths = [track_path(track, root) for track in tracks]
    subtitles = _subtitle_files(spec.subtitle_format, root)
    subtitle_paths = [path for _, path in subtitles]
    _require([*audio_paths, *subtitle_paths])

    args = ["-f", "lavfi", "-i", spec.source]
    for path in (*audio_paths, *subtitle_paths):
        args += ["-i", str(path)]
    args += _map_args(len(audio_paths), len(subtitle_paths))
    args += [*spec.video_args, "-c:a", "copy"]
    if spec.subtitle_format:
        args += ["-c:s", spec.subtitle_format]

    if spec.null_metadata:
        args += _null_metadata_args(len(audio_paths), len(subtitle_paths))
    else:
        args += _metadata_args(
            _audio_tags(spec, tracks), [lang for lang, _ in subtitles]
        )
        args += _container_metadata_args(spec)
    return [*args, *spec.output_args, str(output)]


def _truncate(path: Path, ratio: float) -> None:
    """Recorta el fichero a una fracción de su tamaño."""
    size = path.stat().st_size
    with path.open("r+b") as file:
        file.truncate(int(size * ratio))


def _generate_one(spec: VideoSpec, output_dir: Path) -> Path:
    """Genera un vídeo (y lo trunca si `spec` lo pide)."""
    output = output_dir / spec.filename
    run_ffmpeg(build_ffmpeg_args(spec, output, output_dir))
    if spec.truncate_ratio is not None:
        _truncate(output, spec.truncate_ratio)
    return output


def generate(output_dir: Path = FIXTURES_DIR) -> list[Path]:
    """Genera todos los vídeos definidos en `VIDEOS`.

    Args:
        output_dir: Directorio raíz de fixtures.

    Returns:
        Rutas de los ficheros generados.

    Raises:
        FixtureGenerationError: Si faltan pistas previas o ffmpeg falla.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    return [_generate_one(spec, output_dir) for spec in VIDEOS]


def main() -> None:
    """Genera los fixtures en el directorio por defecto."""
    print_generated(generate())


if __name__ == "__main__":
    main()
