"""Genera los vídeos de prueba a partir de las pistas ya generadas.

Los vídeos incrustan (sin recodificar) las pistas de `audio_tracks` y los
subtítulos de `subtitle_tracks`, que deben existir antes de ejecutar este módulo.
"""

from dataclasses import dataclass
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
            todos los streams (para probar vídeos con metadatos ausentes).
    """

    filename: str
    source: str
    video_args: tuple[str, ...]
    output_args: tuple[str, ...] = ()
    subtitle_format: str | None = None
    null_metadata: bool = False


VIDEOS: tuple[VideoSpec, ...] = (
    VideoSpec(
        filename="simple.mp4",
        source=_mandelbrot(),
        video_args=("-c:v", "libsvtav1", "-crf", "30", "-preset", "8"),
        output_args=("-t", str(DURATION_SECONDS), *FASTSTART),
    ),
    VideoSpec(
        filename="portrait.mp4",
        source=_lavfi("testsrc2", size="720x1280"),
        video_args=(*H264, "-crf", "23", "-vf", "setsar=1"),
        output_args=FASTSTART,
    ),
    VideoSpec(
        filename="metadata.mkv",
        source=_lavfi("testsrc"),
        video_args=H264,
        subtitle_format="ass",
    ),
    VideoSpec(
        filename="test_null_metadata.mkv",
        source=_lavfi("testsrc2"),
        video_args=H264,
        subtitle_format="srt",
        null_metadata=True,
    ),
)


def select_audio(spec: VideoSpec) -> list[TrackSpec]:
    """Selecciona las pistas de audio válidas para el contenedor del vídeo.

    Args:
        spec: Especificación del vídeo.

    Returns:
        Pistas de `TRACKS` compatibles con la extensión de `spec.filename`.
    """
    suffix = Path(spec.filename).suffix
    return [track for track in TRACKS if suffix in track.compatible_with]


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


def _metadata_args(tracks: list[TrackSpec], languages: list[str]) -> list[str]:
    """Metadatos de idioma y título de cada pista de audio y subtítulos."""
    args: list[str] = []
    for i, track in enumerate(tracks):
        args += _stream_metadata("a", i, language=track.language, title=track.title)
    for i, language in enumerate(languages):
        args += _stream_metadata("s", i, language=language, title=f"Sub {language}")
    return args


def _null_metadata_args(n_audio: int, n_subtitles: int) -> list[str]:
    """Vacía metadatos y disposition de todos los streams, y los capítulos."""
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
        args += _metadata_args(tracks, [lang for lang, _ in subtitles])
    return [*args, *spec.output_args, str(output)]


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

    paths: list[Path] = []
    for spec in VIDEOS:
        output = output_dir / spec.filename
        run_ffmpeg(build_ffmpeg_args(spec, output, output_dir))
        paths.append(output)
    return paths


def main() -> None:
    """Genera los fixtures en el directorio por defecto."""
    print_generated(generate())


if __name__ == "__main__":
    main()
