"""Generate multilingual subtitle files for FFmpeg testing."""

from pathlib import Path

OUTPUT_DIR = Path("subtitles_test")
"""Directory where generated subtitle files are stored."""

DURATION_SECONDS = 30
"""Total duration of each subtitle file in seconds."""

EVENT_DURATION_SECONDS = 6
"""Duration of each individual subtitle event in seconds."""

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
        "This message appears for a few seconds.",
        "The complete file lasts exactly thirty seconds.",
        "End of the English test.",
    ],
    "fra": [
        "Bonjour, ceci est un test de sous-titres.",
        "Nous testons FFmpeg avec différentes langues.",
        "Ce message apparaît pendant quelques secondes.",
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


def format_srt_timestamp(seconds: int) -> str:
    """Format seconds using the SRT timestamp format.

    Args:
        seconds: Timestamp in seconds.

    Returns:
        Timestamp formatted as HH:MM:SS,mmm.
    """
    milliseconds = seconds * 1000
    hours, milliseconds = divmod(milliseconds, 3_600_000)
    minutes, milliseconds = divmod(milliseconds, 60_000)
    seconds, milliseconds = divmod(milliseconds, 1000)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def format_ass_timestamp(seconds: int) -> str:
    """Format seconds using the ASS/SSA timestamp format.

    Args:
        seconds: Timestamp in seconds.

    Returns:
        Timestamp formatted as H:MM:SS.cc.
    """
    centiseconds = seconds * 100
    hours, centiseconds = divmod(centiseconds, 360_000)
    minutes, centiseconds = divmod(centiseconds, 6_000)
    seconds, centiseconds = divmod(centiseconds, 100)

    return f"{hours}:{minutes:02d}:{seconds:02d}.{centiseconds:02d}"


def generate_srt(lines: list[str]) -> str:
    """Generate SRT content.

    Args:
        lines: Subtitle texts to include in the file.

    Returns:
        Complete SRT file content.
    """
    output: list[str] = []

    for index, text in enumerate(lines, start=1):
        start = (index - 1) * EVENT_DURATION_SECONDS
        end = index * EVENT_DURATION_SECONDS

        output.extend(
            [
                str(index),
                (f"{format_srt_timestamp(start)} --> {format_srt_timestamp(end)}"),
                text,
                "",
            ]
        )

    return "\n".join(output)


def escape_ass_text(text: str) -> str:
    """Escape characters with special meaning in ASS subtitles.

    Args:
        text: Original subtitle text.

    Returns:
        Escaped subtitle text.
    """
    return text.replace("\\", r"\\").replace("{", r"\{").replace("}", r"\}")


def generate_ass(lines: list[str]) -> str:
    """Generate ASS subtitle content.

    Args:
        lines: Subtitle texts to include in the file.

    Returns:
        Complete ASS file content.
    """
    header = """[Script Info]
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

    events: list[str] = []

    for index, text in enumerate(lines):
        start = index * EVENT_DURATION_SECONDS
        end = (index + 1) * EVENT_DURATION_SECONDS

        events.append(
            "Dialogue: 0,"
            f"{format_ass_timestamp(start)},"
            f"{format_ass_timestamp(end)},"
            f"Default,,0,0,30,,{escape_ass_text(text)}"
        )

    return header + "\n".join(events) + "\n"


def generate_ssa(lines: list[str]) -> str:
    """Generate SSA subtitle content.

    Args:
        lines: Subtitle texts to include in the file.

    Returns:
        Complete SSA file content.
    """
    header = """[Script Info]
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

    events: list[str] = []

    for index, text in enumerate(lines):
        start = index * EVENT_DURATION_SECONDS
        end = (index + 1) * EVENT_DURATION_SECONDS

        events.append(
            "Dialogue: Marked=0,"
            f"{format_ass_timestamp(start)},"
            f"{format_ass_timestamp(end)},"
            f"Default,,0,0,30,,{escape_ass_text(text)}"
        )

    return header + "\n".join(events) + "\n"


def write_subtitle_files(language: str, lines: list[str]) -> None:
    """Write SRT, ASS, and SSA files for one language.

    Args:
        language: ISO 639-2 language code.
        lines: Subtitle texts to write.
    """
    files = {
        "srt": generate_srt(lines),
        "ass": generate_ass(lines),
        "ssa": generate_ssa(lines),
    }

    for extension, content in files.items():
        output_file = OUTPUT_DIR / f"test_{language}.{extension}"
        output_file.write_text(content, encoding="utf-8")


def main() -> None:
    """Generate all subtitle test files."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for language, lines in SUBTITLES.items():
        write_subtitle_files(language, lines)

    generated_files = sorted(OUTPUT_DIR.iterdir())

    print(f"Generated {len(generated_files)} subtitle files:")
    for file in generated_files:
        print(f"  {file}")


if __name__ == "__main__":
    main()
