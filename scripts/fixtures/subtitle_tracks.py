"""Genera ficheros de subtítulos multiidioma (SRT, ASS, SSA) de prueba."""

from collections.abc import Callable
from pathlib import Path

from ._common import FIXTURES_DIR, print_generated

SUBTITLES_DIR_NAME = "subtitles"

# Duración de cada evento; 5 eventos por idioma = 30 s en total.
EVENT_DURATION_SECONDS = 6

SUBTITLES: dict[str, list[str]] = {
    "spa": [
        "Hola, este es un subtítulo de prueba.",
        "Estamos probando FFmpeg con diferentes idiomas.",
        "Este mensaje aparece durante unos segundos.",
        "El archivo completo dura exactamente treinta segundos.",
        "Fin de la prueba en español.",
    ],
    "eng": [
        "Hello, this is a subtitle test.",
        "We are testing FFmpeg with different languages.",
        "This msg appears for a few seconds.",
        "The complete file lasts exactly thirty seconds.",
        "End of the English test.",
    ],
    "fra": [
        "Bonjour, ceci est un test de sous-titres.",
        "Nous testons FFmpeg avec différentes langues.",
        "Ce msg apparaît pendant quelques secondes.",
        "Le fichier complet dure exactement trente secondes.",
        "Fin du test en français.",
    ],
    "deu": [
        "Hallo, dies ist ein Untertiteltest.",
        "Wir testen FFmpeg mit verschiedenen Sprachen.",
        "Diese Nachricht wird einige Sekunden lang angezeigt.",
        "Die vollständige Datei dauert genau dreißig Sekunden.",
        "Ende des deutschen Tests.",
    ],
    "jpn": [
        "こんにちは、字幕のテストです。",
        "さまざまな言語でFFmpegをテストしています。",
        "このメッセージは数秒間表示されます。",
        "ファイル全体の長さはちょうど30秒です。",
        "日本語テストの終了です。",
    ],
    "ara": [
        "مرحبًا، هذا اختبار للترجمة النصية.",
        "نختبر FFmpeg باستخدام لغات مختلفة.",
        "تظهر هذه الرسالة لبضع ثوانٍ.",
        "تبلغ مدة الملف بالكامل ثلاثين ثانية بالضبط.",
        "نهاية الاختبار باللغة العربية.",
    ],
}

ASS_HEADER = """[Script Info]
; Generated automatically for FFmpeg testing
Title: Subtitle test
ScriptType: v4.00+
PlayResX: 1280
PlayResY: 720
Timer: 100.0000

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, \
OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, \
ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, \
MarginR, MarginV, Encoding
Style: Default,Arial,40,&H00FFFFFF,&H0000FFFF,&H00000000,&H80000000,0,0,0,\
0,100,100,0,0,1,2,0,2,20,20,30,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

SSA_HEADER = """[Script Info]
; Generated automatically for FFmpeg testing
Title: Subtitle test
ScriptType: v4.00
PlayResX: 1280
PlayResY: 720
Timer: 100.0000

[V4 Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, \
TertiaryColour, BackColour, Bold, Italic, BorderStyle, Outline, Shadow, \
Alignment, MarginL, MarginR, MarginV, AlphaLevel, Encoding
Style: Default,Arial,40,16777215,65535,0,0,0,0,1,2,0,2,20,20,30,0,1

[Events]
Format: Marked, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


def _split_hms(seconds: int) -> tuple[int, int, int]:
    """Descompone segundos en (horas, minutos, segundos)."""
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return hours, minutes, secs


def format_srt_timestamp(seconds: int) -> str:
    """Formatea segundos con el formato de tiempo de SRT.

    Args:
        seconds: Marca de tiempo en segundos.

    Returns:
        Marca de tiempo con formato HH:MM:SS,mmm.
    """
    hours, minutes, secs = _split_hms(seconds)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},000"


def format_ass_timestamp(seconds: int) -> str:
    """Formatea segundos con el formato de tiempo de ASS/SSA.

    Args:
        seconds: Marca de tiempo en segundos.

    Returns:
        Marca de tiempo con formato H:MM:SS.cc.
    """
    hours, minutes, secs = _split_hms(seconds)
    return f"{hours}:{minutes:02d}:{secs:02d}.00"


def escape_ass_text(text: str) -> str:
    """Escapa los caracteres con significado especial en ASS/SSA.

    Args:
        text: Texto original del subtítulo.

    Returns:
        Texto escapado.
    """
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def _build_dialogues(lines: list[str], marker: str) -> str:
    """Construye las líneas `Dialogue:` (`marker` = Layer en ASS, Marked en SSA)."""
    events: list[str] = []
    for index, text in enumerate(lines):
        start = format_ass_timestamp(index * EVENT_DURATION_SECONDS)
        end = format_ass_timestamp((index + 1) * EVENT_DURATION_SECONDS)
        events.append(
            f"Dialogue: {marker},{start},{end},Default,,0,0,30,,{escape_ass_text(text)}"
        )
    return "\n".join(events) + "\n"


def generate_srt(lines: list[str]) -> str:
    """Genera el contenido SRT.

    Args:
        lines: Textos de los subtítulos.

    Returns:
        Contenido completo del fichero SRT.
    """
    blocks: list[str] = []
    for index, text in enumerate(lines, start=1):
        start = format_srt_timestamp((index - 1) * EVENT_DURATION_SECONDS)
        end = format_srt_timestamp(index * EVENT_DURATION_SECONDS)
        blocks.append(f"{index}\n{start} --> {end}\n{text}\n")
    return "\n".join(blocks)


def generate_ass(lines: list[str]) -> str:
    """Genera el contenido ASS.

    Args:
        lines: Textos de los subtítulos.

    Returns:
        Contenido completo del fichero ASS.
    """
    return ASS_HEADER + _build_dialogues(lines, marker="0")


def generate_ssa(lines: list[str]) -> str:
    """Genera el contenido SSA.

    Args:
        lines: Textos de los subtítulos.

    Returns:
        Contenido completo del fichero SSA.
    """
    return SSA_HEADER + _build_dialogues(lines, marker="Marked=0")


GENERATORS: dict[str, Callable[[list[str]], str]] = {
    "srt": generate_srt,
    "ass": generate_ass,
    "ssa": generate_ssa,
}


def subtitle_path(
    language: str, extension: str, output_dir: Path = FIXTURES_DIR
) -> Path:
    """Devuelve la ruta donde se genera (o se espera) un fichero de subtítulos.

    Args:
        language: Código de idioma ISO 639-2.
        extension: Formato del subtítulo (`srt`, `ass` o `ssa`).
        output_dir: Directorio raíz de fixtures.

    Returns:
        Ruta del fichero de subtítulos.
    """
    return output_dir / SUBTITLES_DIR_NAME / f"test_{language}.{extension}"


def write_subtitle_files(
    language: str, lines: list[str], output_dir: Path
) -> list[Path]:
    """Escribe los ficheros SRT, ASS y SSA de un idioma.

    Args:
        language: Código de idioma ISO 639-2.
        lines: Textos de los subtítulos.
        output_dir: Directorio raíz de fixtures.

    Returns:
        Rutas de los ficheros escritos.
    """
    paths: list[Path] = []
    for extension, generator in GENERATORS.items():
        path = subtitle_path(language, extension, output_dir)
        path.write_text(generator(lines), encoding="utf-8")
        paths.append(path)
    return paths


def generate(output_dir: Path = FIXTURES_DIR) -> list[Path]:
    """Genera todos los ficheros de subtítulos de prueba.

    Args:
        output_dir: Directorio raíz de fixtures.

    Returns:
        Rutas de los ficheros generados.
    """
    (output_dir / SUBTITLES_DIR_NAME).mkdir(parents=True, exist_ok=True)

    paths: list[Path] = []
    for language, lines in SUBTITLES.items():
        paths += write_subtitle_files(language, lines, output_dir)
    return paths


def main() -> None:
    """Genera los fixtures en el directorio por defecto."""
    print_generated(generate())


if __name__ == "__main__":
    main()
