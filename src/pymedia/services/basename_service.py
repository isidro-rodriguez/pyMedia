import re
from pathlib import Path

from pymedia.data import CONTAINERS_BY_CODEC, GIF_EXTENSION, VIDEO_EXTENSIONS
from pymedia.feedback.errors import (
    CannotCreateDirectoryError,
    InvalidDirectoryError,
    InvalidFileExtensionError,
    InvalidFileNameError,
    MissingMediaPropertyError,
)
from pymedia.models.arguments import CommandName


def _format_supported(extensions: set[str] | list[str]) -> str:
    """Formatea extensiones como lista legible para mensajes."""
    return ", ".join(sorted(extensions))


def _is_valid_video_extension(video: Path) -> bool:
    if video.suffix is None:
        raise InvalidFileExtensionError(
            extension=None, supported=_format_supported(VIDEO_EXTENSIONS)
        )
    if video.suffix not in VIDEO_EXTENSIONS:
        raise InvalidFileExtensionError(
            extension=video.suffix,
            supported=_format_supported(VIDEO_EXTENSIONS),
        )
    return True


def _is_valid_filename(name: str) -> bool:
    return bool(
        name
        and not re.search(r'[<>:"/\\|?*\x00-\x1F]', name)
        and not name.endswith((" ", "."))
        and name.upper().split(".")[0]
        not in {
            "CON",
            "PRN",
            "AUX",
            "NUL",
            "COM1",
            "COM2",
            "COM3",
            "COM4",
            "COM5",
            "COM6",
            "COM7",
            "COM8",
            "COM9",
            "LPT1",
            "LPT2",
            "LPT3",
            "LPT4",
            "LPT5",
            "LPT6",
            "LPT7",
            "LPT8",
            "LPT9",
        }
    )


def process_inputs(inputs: list[Path]) -> list[Path]:
    for i in inputs:
        _is_valid_video_extension(i)
    return inputs


def process_output(
    output: Path,
    command: str,
    target_codec: str | None = None,
) -> Path:
    """Comprueba el fichero de salida tenga un nombre y extensión válido."""
    # Crear directorios intermedios si no existen
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise CannotCreateDirectoryError(path=output.parent) from e

    # Comprobación del directorio (solo si se va a crear/escritura en subdirectorio)
    if output.parent != Path(".") and not _is_valid_filename(output.parent.name):
        raise InvalidDirectoryError(directory=output.parent.name)

    # Comprobación del nombre de fichero
    if output.stem is None:
        raise InvalidFileNameError(filename=None)
    if not _is_valid_filename(output.stem):
        raise InvalidFileNameError(filename=output.stem)

    # Comprobación de la extensión
    if output.suffix is None:
        raise InvalidFileExtensionError(
            extension="", supported=_format_supported(VIDEO_EXTENSIONS)
        )

    if command is CommandName.GIF:
        if output.suffix != GIF_EXTENSION[0]:
            raise InvalidFileExtensionError(
                extension=output.suffix,
                supported=_format_supported(GIF_EXTENSION),
            )
    else:
        if output.suffix not in VIDEO_EXTENSIONS:
            raise InvalidFileExtensionError(
                extension=output.suffix,
                supported=_format_supported(VIDEO_EXTENSIONS),
            )

        if target_codec is None:
            raise MissingMediaPropertyError(property_name="Video codec")

        valid_containers = CONTAINERS_BY_CODEC.get(target_codec, set())
        if valid_containers and output.suffix not in valid_containers:
            raise InvalidFileExtensionError(
                extension=output.suffix,
                supported=_format_supported(valid_containers),
            )

    return output
