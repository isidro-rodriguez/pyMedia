"""Utilidades compartidas por las suites de tests de la CLI de pyMedia.

Contiene el contrato de invocación (`Invoke`/`CliResult`) que permite ejecutar
el mismo test contra la superficie Typer y contra el binario compilado, y los
helpers de inspección de ficheros basados en ffprobe.
"""

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol, cast

# =============================================================================
#  Contrato de invocación
# =============================================================================


@dataclass(frozen=True)
class CliResult:
    """Resultado normalizado de una ejecución de pyMedia.

    Attributes:
        exit_code: Código de salida del proceso o del `CliRunner`.
        output: stdout y stderr combinados, para aserciones sobre mensajes.
    """

    exit_code: int
    output: str


class Invoke(Protocol):
    """Ejecutor de pyMedia: `pymedia("info", "video.mp4")`."""

    def __call__(self, *args: str, input: str | None = None) -> CliResult:
        """Ejecuta pyMedia con los argumentos dados.

        Args:
            *args: Argumentos de línea de comandos, sin el nombre del programa.
            input: Texto a enviar por stdin (respuestas a `typer.confirm`).

        Returns:
            Código de salida y salida combinada.
        """
        ...


# =============================================================================
#  Inspección con ffprobe
# =============================================================================


def _ffprobe(path: Path, show: str) -> dict[str, Any]:
    """Ejecuta ffprobe con el `-show_*` indicado y devuelve su JSON."""
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "quiet",
            "-print_format",
            "json",
            f"-show_{show}",
            str(path),
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    )
    return cast(dict[str, Any], json.loads(result.stdout))


def ffprobe_streams(path: Path) -> list[dict[str, Any]]:
    """Devuelve los streams que ffprobe detecta en el fichero indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.

    Returns:
        Streams del fichero en formato JSON de ffprobe.
    """
    return cast(list[dict[str, Any]], _ffprobe(path, "streams")["streams"])


def ffprobe_duration(path: Path) -> float:
    """Devuelve la duración total, en segundos, del fichero indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.

    Returns:
        Duración total del fichero en segundos.
    """
    return float(_ffprobe(path, "format")["format"]["duration"])


def stream_types(path: Path) -> list[str | None]:
    """Lista los tipos de stream (video/audio/subtitle) del fichero indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.

    Returns:
        Tipos de stream en el orden que reporta ffprobe.
    """
    return [stream.get("codec_type") for stream in ffprobe_streams(path)]


def streams_of(path: Path, stream_type: str) -> list[dict[str, Any]]:
    """Filtra los streams del fichero por tipo.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.
        stream_type: Tipo de stream (video/audio/subtitle).

    Returns:
        Streams del tipo indicado, en el orden que reporta ffprobe.
    """
    return [s for s in ffprobe_streams(path) if s.get("codec_type") == stream_type]


def stream_tag(path: Path, stream_type: str, tag: str, index: int = 0) -> str | None:
    """Devuelve un tag del stream indicado según su tipo y posición local.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.
        stream_type: Tipo de stream (video/audio/subtitle).
        tag: Nombre del tag (p. ej. `language` o `title`).
        index: Índice local dentro del tipo de stream.

    Returns:
        Valor del tag, o `None` si no está presente.
    """
    tags = streams_of(path, stream_type)[index].get("tags") or {}
    return cast(str | None, tags.get(tag))


def stream_codec_names(path: Path, stream_type: str) -> list[str | None]:
    """Lista los códecs de los streams del tipo indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.
        stream_type: Tipo de stream (video/audio/subtitle).

    Returns:
        Nombres de códec en el orden que reporta ffprobe.
    """
    return [s.get("codec_name") for s in streams_of(path, stream_type)]


def stream_disposition(path: Path, stream_type: str, flag: str, index: int = -1) -> int:
    """Devuelve un flag de disposición del stream indicado.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.
        stream_type: Tipo de stream (video/audio/subtitle).
        flag: Nombre del flag (p. ej. `default` o `forced`).
        index: Índice local dentro del tipo de stream (por defecto, el último).

    Returns:
        `1` si el flag está activo, `0` en caso contrario.
    """
    disposition = streams_of(path, stream_type)[index].get("disposition") or {}
    return int(disposition.get(flag, 0))


def video_size(path: Path) -> tuple[int, int]:
    """Devuelve `(ancho, alto)` del primer stream de vídeo o imagen.

    Args:
        path: Ruta del fichero multimedia a inspeccionar.

    Returns:
        Dimensiones en píxeles.
    """
    stream = streams_of(path, "video")[0]
    return int(stream["width"]), int(stream["height"])
