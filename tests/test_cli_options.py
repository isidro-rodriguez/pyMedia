"""Tests parametrizados de las opciones que comparten varios comandos.

Cada familia (overwrite, `--debug`, filtros de imagen, flags de pista...) se
escribe una sola vez y se ejecuta contra todos los comandos que la exponen.
Como el resto de la suite CLI, usan la fixture `pymedia`, así que cada caso
corre como CLI en proceso (`[cli]`) y como binario compilado (`[binary]`).
"""

from dataclasses import dataclass
from pathlib import Path

import pytest
from helpers import Invoke, stream_disposition, stream_tag, video_size

# =============================================================================
#  Catálogo de comandos: una invocación mínima y válida de cada uno
# =============================================================================


@dataclass(frozen=True)
class Command:
    """Invocación mínima de un comando de pyMedia.

    Attributes:
        name: Nombre del subcomando.
        inputs: Nombres de las fixtures de entrada, en orden posicional.
        args: Opciones obligatorias del comando para que la ejecución sea válida.
        suffix: Extensión de la salida, o `None` si el comando no escribe ficheros.
    """

    name: str
    inputs: tuple[str, ...]
    args: tuple[str, ...] = ()
    suffix: str | None = None


COMMANDS: dict[str, Command] = {
    c.name: c
    for c in (
        Command("info", ("video_mp4_a",)),
        Command("sheet", ("video_mp4_a",), (), ".jpg"),
        Command("join", ("video_mp4_a", "video_mp4_b"), (), ".mp4"),
        Command("remux", ("video_mp4_a",), (), ".mkv"),
        Command("cut", ("video_mp4_a",), ("--at", "00:00:01"), ".mp4"),
        Command("transcode", ("video_mp4_a",), ("--video",), ".mp4"),
        Command(
            "add-audio",
            ("video_mkv", "audio_m4a"),
            ("--language", "eng"),
            ".mkv",
        ),
        Command("delete-audio", ("video_mkv",), ("--tracks", "0"), ".mkv"),
        Command(
            "edit-audio",
            ("video_mkv",),
            ("--track", "0", "--language", "fre"),
            ".mkv",
        ),
        Command("extract-audio", ("video_mkv",), ("--tracks", "0"), ".m4a"),
        Command(
            "add-subs",
            ("video_mkv", "subs_spa"),
            ("--language", "spa"),
            ".mkv",
        ),
        Command("delete-subs", ("video_mkv_subs",), ("--tracks", "0"), ".mkv"),
        Command(
            "edit-subs",
            ("video_mkv_subs",),
            ("--track", "0", "--language", "fre"),
            ".mkv",
        ),
        Command("extract-subs", ("video_mkv_subs",), ("--tracks", "0"), ".srt"),
        Command("animated", ("video_mp4_a",), (), ".gif"),
        Command("frames", ("video_mp4_a",), ("--at", "00:00:01"), ".jpg"),
        Command("interval", ("video_mp4_a",), ("--every", "1"), ".jpg"),
        Command("scene", ("video_scenes",), (), ".jpg"),
    )
}

ALL = list(COMMANDS)
WRITING = [name for name, cmd in COMMANDS.items() if cmd.suffix]
# Comandos que aplican filtros de imagen (`--crop`, `--rotate`, `--size`...).
VISUAL = ["animated", "frames", "interval", "scene", "transcode"]


def build_args(
    cmd: Command,
    request: pytest.FixtureRequest,
    output: Path | None = None,
    *extra: str,
) -> list[str]:
    """Construye los argumentos de una invocación válida del comando.

    Args:
        cmd: Comando del catálogo.
        request: Request del test, para resolver las fixtures de entrada.
        output: Ruta de salida (`-o`); se omite si es `None`.
        *extra: Opciones adicionales a añadir al final.

    Returns:
        Argumentos de línea de comandos, sin el nombre del programa.
    """
    inputs = [str(request.getfixturevalue(name)) for name in cmd.inputs]
    args = [cmd.name, *inputs, *cmd.args]
    if output is not None:
        args += ["-o", str(output)]
    return [*args, *extra]


def outputs_of(directory: Path) -> list[Path]:
    """Lista los ficheros generados en el directorio (ignora temporales ocultos)."""
    return sorted(p for p in directory.iterdir() if p.is_file())


# =============================================================================
#  Validación de entradas y ayuda
# =============================================================================


@pytest.mark.parametrize("name", ALL)
def test_input_not_a_file(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """Todos los comandos rechazan un vídeo de entrada que no existe."""
    args = build_args(COMMANDS[name], request)
    args[1] = str(tmp_path / "missing.mp4")

    result = pymedia(*args)

    assert result.exit_code != 0
    assert "is not a file" in result.output


@pytest.mark.parametrize("name", ALL)
def test_input_invalid_extension(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """Todos los comandos rechazan una entrada con extensión no soportada."""
    notes = tmp_path / "notes.txt"
    notes.write_text("no soy un vídeo", encoding="utf-8")
    args = build_args(COMMANDS[name], request)
    args[1] = str(notes)

    result = pymedia(*args)

    assert result.exit_code != 0
    assert "Invalid extension .txt" in result.output


@pytest.mark.parametrize("name", ALL)
def test_help_option(pymedia: Invoke, name: str) -> None:
    """`<comando> --help` muestra el uso y sale sin error."""
    result = pymedia(name, "--help")

    assert result.exit_code == 0
    assert "Usage:" in result.output
    assert "--help" in result.output


@pytest.mark.parametrize("name", ALL)
def test_no_arguments_shows_help(pymedia: Invoke, name: str) -> None:
    """`<comando>` sin argumentos muestra la ayuda en vez de un traceback."""
    result = pymedia(name)

    # El código de salida (0 o 2) depende de la versión de Click.
    assert "Usage:" in result.output
    assert "Traceback" not in result.output


# =============================================================================
#  Política de sobrescritura (--overwrite / -ov)
# =============================================================================

OVERWRITE_CASES = [
    pytest.param("no", None, False, id="no"),
    pytest.param("ask", "n\n", False, id="ask-decline"),
    pytest.param("ask", "y\n", True, id="ask-accept"),
    pytest.param("yes", None, True, id="yes"),
]
STALE = b"existing"


@pytest.mark.parametrize("name", WRITING)
@pytest.mark.parametrize(("policy", "answer", "replaced"), OVERWRITE_CASES)
def test_overwrite_policy(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    policy: str,
    answer: str | None,
    replaced: bool,
    tmp_path: Path,
) -> None:
    """`--overwrite` respeta o reemplaza las salidas ya existentes.

    Se genera la salida real una vez (así el test no depende del nombre exacto
    de los ficheros derivados) y se marca como obsoleta para ver si se toca.
    """
    cmd = COMMANDS[name]
    output = tmp_path / f"out{cmd.suffix}"
    assert pymedia(*build_args(cmd, request, output, "-ov", "yes")).exit_code == 0
    produced = outputs_of(tmp_path)
    assert produced
    for file in produced:
        file.write_bytes(STALE)

    result = pymedia(*build_args(cmd, request, output, "-ov", policy), input=answer)

    assert result.exit_code == 0
    assert outputs_of(tmp_path) == produced
    assert all((f.read_bytes() != STALE) is replaced for f in produced)
    if not replaced:
        assert "Process skipped" in result.output


@pytest.mark.parametrize("name", WRITING)
@pytest.mark.parametrize("option", ["-ov", "--overwrite"])
def test_overwrite_rejects_unknown_policy(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    option: str,
    tmp_path: Path,
) -> None:
    """`--overwrite` solo admite `yes`, `no` y `ask`."""
    output = tmp_path / f"out{COMMANDS[name].suffix}"

    result = pymedia(*build_args(COMMANDS[name], request, output, option, "never"))

    assert result.exit_code != 0
    assert "Invalid value for '--overwrite' / '-ov'" in result.output
    assert not output.exists()


# =============================================================================
#  Modo depuración (--debug)
# =============================================================================


@pytest.mark.parametrize("name", WRITING)
def test_debug_declined_does_not_run_ffmpeg(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--debug` pide confirmación y, si se rechaza, no genera salidas."""
    output = tmp_path / f"out{COMMANDS[name].suffix}"

    result = pymedia(
        *build_args(COMMANDS[name], request, output, "--debug"), input="n\n"
    )

    assert result.exit_code == 0
    assert "User decided to abort process" in result.output
    assert outputs_of(tmp_path) == []


@pytest.mark.parametrize("name", WRITING)
def test_debug_accepted_runs_ffmpeg(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--debug` ejecuta el comando ffmpeg mostrado si se confirma."""
    output = tmp_path / f"out{COMMANDS[name].suffix}"

    # Algunos comandos lanzan varios ffmpeg: una confirmación por cada uno.
    result = pymedia(
        *build_args(COMMANDS[name], request, output, "--debug"), input="y\n" * 10
    )

    assert result.exit_code == 0
    assert "Do you want to run this ffmpeg command?" in result.output
    assert outputs_of(tmp_path)


# =============================================================================
#  Filtros de imagen compartidos (crop, rotate, size, mode, upscale, flips)
# =============================================================================

# Vídeo de entrada: 160x90. Se comprueban las dimensiones del resultado.
FILTER_CASES = [
    pytest.param(("--crop", "80,44,0,0"), (80, 44), id="crop"),
    pytest.param(("--rotate", "90"), (90, 160), id="rotate-90"),
    pytest.param(("--rotate", "180"), (160, 90), id="rotate-180"),
    pytest.param(("--rotate", "270"), (90, 160), id="rotate-270"),
    pytest.param(("--size", "64x36"), (64, 36), id="size-downscale"),
    pytest.param(("--size", "320x180", "--upscale"), (320, 180), id="upscale"),
    pytest.param(("--size", "80x80", "--mode", "stretch"), (80, 80), id="mode-stretch"),
    pytest.param(("--size", "100x100", "--mode", "fit"), (100, 56), id="mode-fit"),
    pytest.param(("--size", "80x80", "--mode", "cover"), (142, 80), id="mode-cover"),
    pytest.param(("--hflip",), (160, 90), id="hflip"),
    pytest.param(("--vflip",), (160, 90), id="vflip"),
]


@pytest.mark.parametrize("name", VISUAL)
@pytest.mark.parametrize(("options", "expected"), FILTER_CASES)
def test_image_filter_applies(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    options: tuple[str, ...],
    expected: tuple[int, int],
    tmp_path: Path,
) -> None:
    """Los filtros de imagen dejan la salida con las dimensiones esperadas."""
    cmd = COMMANDS[name]
    output = tmp_path / f"out{cmd.suffix}"

    result = pymedia(*build_args(cmd, request, output, "-ov", "yes", *options))

    assert result.exit_code == 0
    produced = outputs_of(tmp_path)
    assert produced
    if name == "transcode":
        # El re-escalado de vídeo fuerza dimensiones pares (compatibilidad de
        # códecs), p. ej. el modo `fit` de 100x100 da 100x56.
        expected = (expected[0] // 2 * 2, expected[1] // 2 * 2)
    assert {video_size(file) for file in produced} == {expected}


IMAGE_COMMANDS = ["animated", "frames", "interval", "scene"]
ODD_CASES = [
    pytest.param(("--crop", "81,45,0,0"), (81, 45), id="crop"),
    pytest.param(("--size", "80x45"), (80, 45), id="size"),
]


@pytest.mark.parametrize("name", IMAGE_COMMANDS)
@pytest.mark.parametrize(("options", "expected"), ODD_CASES)
def test_image_keeps_odd_dimensions(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    options: tuple[str, ...],
    expected: tuple[int, int],
    tmp_path: Path,
) -> None:
    """Las imágenes conservan dimensiones impares (solo el vídeo exige pares).

    Falla hasta que se retire en `src/` la limitación de dimensiones pares
    para salidas que no son vídeo.
    """
    cmd = COMMANDS[name]
    output = tmp_path / f"out{cmd.suffix}"

    result = pymedia(*build_args(cmd, request, output, "-ov", "yes", *options))

    assert result.exit_code == 0
    assert {video_size(f) for f in outputs_of(tmp_path)} == {expected}


def test_transcode_rejects_odd_target_dimensions(
    pymedia: Invoke, request: pytest.FixtureRequest, tmp_path: Path
) -> None:
    """`transcode --size` con dimensiones impares se rechaza (vídeo)."""
    output = tmp_path / "out.mp4"

    result = pymedia(
        *build_args(COMMANDS["transcode"], request, output, "--size", "81x45")
    )

    assert result.exit_code != 0
    assert "Target dimensions must be even" in result.output


@pytest.mark.parametrize("name", VISUAL)
def test_crop_bigger_than_video_is_rejected(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--crop` rechaza un área que se sale de las dimensiones del vídeo."""
    output = tmp_path / f"out{COMMANDS[name].suffix}"

    result = pymedia(
        *build_args(
            COMMANDS[name], request, output, "-ov", "yes", "--crop", "160,90,10,10"
        )
    )

    assert result.exit_code != 0
    assert "Invalid crop area" in result.output


@pytest.mark.parametrize("name", VISUAL)
def test_crop_zero_dimensions_is_rejected(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--crop` rechaza dimensiones de recorte iguales a cero."""
    output = tmp_path / f"out{COMMANDS[name].suffix}"

    result = pymedia(
        *build_args(COMMANDS[name], request, output, "-ov", "yes", "--crop", "0,0,0,0")
    )

    assert result.exit_code != 0
    assert "Invalid crop dimensions" in result.output


@pytest.mark.parametrize("name", VISUAL)
def test_crop_invalid_format_is_rejected(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--crop` rechaza formatos que no son WIDTH,HEIGHT,X,Y."""
    output = tmp_path / f"out{COMMANDS[name].suffix}"

    result = pymedia(
        *build_args(COMMANDS[name], request, output, "-ov", "yes", "--crop", "abc")
    )

    assert result.exit_code != 0
    assert "Invalid crop" in result.output


@pytest.mark.parametrize("name", VISUAL)
def test_crop_exceeds_video_height_is_rejected(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--crop` rechaza un área que se sale de la altura del vídeo."""
    output = tmp_path / f"out{COMMANDS[name].suffix}"

    result = pymedia(
        *build_args(
            COMMANDS[name], request, output, "-ov", "yes", "--crop", "10,80,0,11"
        )
    )

    assert result.exit_code != 0
    assert "Invalid crop area" in result.output


@pytest.mark.parametrize("name", VISUAL)
def test_oversize_without_upscale_is_ignored(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--size` mayor que el vídeo sin `--upscale` se ignora con un aviso."""
    output = tmp_path / f"out{COMMANDS[name].suffix}"

    result = pymedia(
        *build_args(COMMANDS[name], request, output, "-ov", "yes", "--size", "320x180")
    )

    assert result.exit_code == 0
    assert "Ignored scale" in result.output
    assert {video_size(f) for f in outputs_of(tmp_path)} == {(160, 90)}


# Opción de cada comando que fija un instante, y un valor mayor que la duración.
LATE_TIMESTAMP = [
    pytest.param("animated", ("--start", "00:00:03"), id="animated"),
    pytest.param("frames", ("--at", "00:00:03"), id="frames"),
    pytest.param("interval", ("--start", "00:00:03"), id="interval"),
    pytest.param("scene", ("--start", "00:00:04"), id="scene"),
]


@pytest.mark.parametrize(("name", "late"), LATE_TIMESTAMP)
def test_timestamp_beyond_duration_is_rejected(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    late: tuple[str, ...],
    tmp_path: Path,
) -> None:
    """Un instante posterior a la duración del vídeo se rechaza.

    Para `frames`, `--at` se repite y prevalece el último valor.
    """
    cmd = COMMANDS[name]
    output = tmp_path / f"out{cmd.suffix}"

    result = pymedia(*build_args(cmd, request, output, "-ov", "yes", *late))

    assert result.exit_code != 0
    assert "exceeds video duration" in result.output


# Comandos con --start/--end (TimestampStartEndMixin expuesto en CLI)
# Usamos marcas dentro de la duración del vídeo (2 s).
START_END_COMMANDS = [
    pytest.param("animated", id="animated"),
    pytest.param("interval", id="interval"),
    pytest.param("scene", id="scene"),
]


@pytest.mark.parametrize("name", START_END_COMMANDS)
def test_start_after_end_is_rejected(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--start` posterior a `--end` se rechaza."""
    cmd = COMMANDS[name]
    output = tmp_path / f"out{cmd.suffix}"

    result = pymedia(
        *build_args(
            cmd,
            request,
            output,
            "-ov",
            "yes",
            "--start",
            "00:00:01.5",
            "--end",
            "00:00:01",
        )
    )

    assert result.exit_code != 0
    assert "Invalid timestamps" in result.output
    assert "Start" in result.output and "End" in result.output


# Test específico para cut con --start/--end (tiene --at por defecto en COMMANDS)
def test_cut_start_after_end_is_rejected(
    pymedia: Invoke, request: pytest.FixtureRequest, tmp_path: Path
) -> None:
    """`cut --start` posterior a `--end` se rechaza."""
    cmd = COMMANDS["cut"]
    output = tmp_path / f"out{cmd.suffix}"

    # build_args incluye --at por defecto; lo llamamos sin él
    inputs = [str(request.getfixturevalue(n)) for n in cmd.inputs]
    args = [
        "cut",
        *inputs,
        "--start",
        "00:00:01.5",
        "--end",
        "00:00:01",
        "-o",
        str(output),
        "-ov",
        "yes",
    ]

    result = pymedia(*args)

    assert result.exit_code != 0
    assert "Invalid timestamps" in result.output
    assert "Start" in result.output and "End" in result.output


# Comandos con --at (TimestampAtMixin expuesto en CLI)
# Usamos marcas dentro de la duración del vídeo (2 s).
AT_COMMANDS = [
    pytest.param("cut", id="cut"),
    pytest.param("frames", id="frames"),
]


@pytest.mark.parametrize("name", AT_COMMANDS)
def test_at_descending_is_rejected(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--at` con marcas en orden descendente se rechaza."""
    cmd = COMMANDS[name]
    output = tmp_path / f"out{cmd.suffix}"

    # Para cut, hay que anular el --at por defecto
    if name == "cut":
        inputs = [str(request.getfixturevalue(n)) for n in cmd.inputs]
        args = [
            "cut",
            *inputs,
            "--at",
            "00:00:01.5,00:00:01",
            "-o",
            str(output),
            "-ov",
            "yes",
        ]
        result = pymedia(*args)
    else:
        result = pymedia(
            *build_args(
                cmd, request, output, "-ov", "yes", "--at", "00:00:01.5,00:00:01"
            )
        )

    assert result.exit_code != 0
    assert "ascending order" in result.output


@pytest.mark.parametrize("name", AT_COMMANDS)
def test_at_invalid_format_is_rejected(
    pymedia: Invoke, request: pytest.FixtureRequest, name: str, tmp_path: Path
) -> None:
    """`--at` con formato inválido se rechaza."""
    cmd = COMMANDS[name]
    output = tmp_path / f"out{cmd.suffix}"

    if name == "cut":
        inputs = [str(request.getfixturevalue(n)) for n in cmd.inputs]
        args = ["cut", *inputs, "--at", "abc", "-o", str(output), "-ov", "yes"]
        result = pymedia(*args)
    else:
        result = pymedia(*build_args(cmd, request, output, "-ov", "yes", "--at", "abc"))

    assert result.exit_code != 0
    assert "Invalid timestamp format" in result.output


# =============================================================================
#  Flags de pista (audio y subtítulos)
# =============================================================================
AUDIO_FLAGS = [
    ("--forced", "forced"),
    ("--default", "default"),
    ("--hearing-impaired", "hearing_impaired"),
    ("--commentary", "comment"),
]
SUBS_FLAGS = [
    ("--forced", "forced"),
    ("--default", "default"),
    ("--hearing-impaired", "hearing_impaired"),
    ("--visual-impaired", "visual_impaired"),
]
TRACK_FLAG_CASES = [
    pytest.param(add, edit, kind, option, flag, id=f"{kind}{option}")
    for kind, add, edit, flags in (
        ("audio", "add-audio", "edit-audio", AUDIO_FLAGS),
        ("subtitle", "add-subs", "edit-subs", SUBS_FLAGS),
    )
    for option, flag in flags
]


@pytest.mark.parametrize(("add", "edit", "kind", "option", "flag"), TRACK_FLAG_CASES)
def test_add_track_sets_flag(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    add: str,
    edit: str,
    kind: str,
    option: str,
    flag: str,
    tmp_path: Path,
) -> None:
    """`add-audio`/`add-subs` marcan la pista nueva con el flag indicado."""
    output = tmp_path / "out.mkv"

    result = pymedia(*build_args(COMMANDS[add], request, output, "-ov", "yes", option))

    assert result.exit_code == 0
    assert stream_disposition(output, kind, flag) == 1


@pytest.mark.parametrize(("add", "edit", "kind", "option", "flag"), TRACK_FLAG_CASES)
def test_edit_track_sets_and_clears_flag(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    add: str,
    edit: str,
    kind: str,
    option: str,
    flag: str,
    tmp_path: Path,
) -> None:
    """`edit-*` activa un flag y `--no-<flag>` lo vuelve a desactivar."""
    cmd = COMMANDS[edit]
    marked = tmp_path / "marked.mkv"
    cleared = tmp_path / "cleared.mkv"
    negated = option.replace("--", "--no-", 1)

    first = pymedia(*build_args(cmd, request, marked, "-ov", "yes", option))
    second = pymedia(
        "edit-audio" if kind == "audio" else "edit-subs",
        str(marked),
        "--track",
        "0",
        negated,
        "-o",
        str(cleared),
        "-ov",
        "yes",
    )

    assert first.exit_code == 0
    assert stream_disposition(marked, kind, flag, index=0) == 1
    assert second.exit_code == 0
    assert stream_disposition(cleared, kind, flag, index=0) == 0


TRACK_TITLE_CASES = [
    pytest.param("add-audio", "audio", -1, id="add-audio"),
    pytest.param("edit-audio", "audio", 0, id="edit-audio"),
    pytest.param("add-subs", "subtitle", -1, id="add-subs"),
    pytest.param("edit-subs", "subtitle", 0, id="edit-subs"),
]


@pytest.mark.parametrize(("name", "kind", "index"), TRACK_TITLE_CASES)
def test_track_title(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    kind: str,
    index: int,
    tmp_path: Path,
) -> None:
    """`--title` fija el título de la pista en `add-*` y `edit-*`."""
    output = tmp_path / "out.mkv"

    result = pymedia(
        *build_args(
            COMMANDS[name], request, output, "-ov", "yes", "--title", "My Title"
        )
    )

    assert result.exit_code == 0
    assert stream_tag(output, kind, "title", index) == "My Title"


# =============================================================================
#  Rutas de salida (WRITING)
# =============================================================================


@pytest.mark.parametrize("name", WRITING)
def test_output_unsupported_extension(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    tmp_path: Path,
) -> None:
    """Salida con extensión no soportada lanza error."""
    cmd = COMMANDS[name]
    output = tmp_path / "out.bmp"

    result = pymedia(*build_args(cmd, request, output, "-ov", "yes"))

    assert result.exit_code != 0


@pytest.mark.parametrize("name", WRITING)
def test_output_special_chars(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    tmp_path: Path,
) -> None:
    """Salida con espacios en la ruta funciona."""
    cmd = COMMANDS[name]
    output = tmp_path / "output dir" / f"out{cmd.suffix}"

    result = pymedia(*build_args(cmd, request, output, "-ov", "yes"))

    assert result.exit_code == 0


# =============================================================================
#  --tracks / --track
# =============================================================================

TRACK_PARSE_CASES = [
    pytest.param("--tracks", "a,b", id="tracks-malformed"),
    pytest.param("--tracks", "", id="tracks-empty"),
]


@pytest.mark.parametrize("option,value", TRACK_PARSE_CASES)
@pytest.mark.parametrize(
    "name",
    ["extract-audio", "delete-subs", "edit-audio", "edit-subs"],
)
def test_track_malformed(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    option: str,
    value: str,
    tmp_path: Path,
) -> None:
    """`--tracks`/`--track` con valores mal formados lanza error."""
    cmd = COMMANDS[name]
    output = tmp_path / "out.mkv"

    result = pymedia(*build_args(cmd, request, output, "-ov", "yes", option, value))

    assert result.exit_code != 0


INDEX_OUT_OF_RANGE = [
    pytest.param("extract-audio", "--tracks", "99", id="extract-audio"),
    pytest.param("extract-subs", "--tracks", "99", id="extract-subs"),
    pytest.param("edit-audio", "--track", "99", id="edit-audio"),
    pytest.param("edit-subs", "--track", "99", id="edit-subs"),
    pytest.param("delete-subs", "--tracks", "99", id="delete-subs"),
]


@pytest.mark.parametrize("name,option,value", INDEX_OUT_OF_RANGE)
def test_track_index_out_of_range(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    option: str,
    value: str,
    tmp_path: Path,
) -> None:
    """`--tracks`/`--track` con índice fuera de rango lanza error."""
    cmd = COMMANDS[name]
    output = tmp_path / "out.mkv"

    result = pymedia(*build_args(cmd, request, output, "-ov", "yes", option, value))

    assert result.exit_code != 0


# =============================================================================
#  --language inválido
# =============================================================================

LANGUAGE_CASES = [
    pytest.param("add-audio", "--language", "xyz", id="add-audio"),
    pytest.param("edit-audio", "--language", "xyz", id="edit-audio"),
    pytest.param("add-subs", "--language", "xyz", id="add-subs"),
    pytest.param("edit-subs", "--language", "xyz", id="edit-subs"),
]


@pytest.mark.parametrize("name,option,value", LANGUAGE_CASES)
def test_language_invalid(
    pymedia: Invoke,
    request: pytest.FixtureRequest,
    name: str,
    option: str,
    value: str,
    tmp_path: Path,
) -> None:
    """`--language` con código ISO 639-2 inválido lanza error."""
    cmd = COMMANDS[name]
    output = tmp_path / "out.mkv"

    result = pymedia(*build_args(cmd, request, output, "-ov", "yes", option, value))

    assert result.exit_code != 0
