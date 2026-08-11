import re
from pathlib import Path

from pymedia.data import CONTAINERS_BY_CODEC, GIF_EXTENSION, VIDEO_EXTENSIONS
from pymedia.models.arguments import CommandName
from pymedia.models.errors import (
    InvalidFileExtensionError,
    InvalidFilenameError,
    MissingMediaPropertyError,
)


def _is_valid_video_extension(video: Path) -> bool:
    if video.suffix is None:
        raise InvalidFileExtensionError(None, None)
    if video.suffix not in VIDEO_EXTENSIONS:
        raise InvalidFileExtensionError(video.suffix, VIDEO_EXTENSIONS)
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
    if output.stem is None:
        raise InvalidFilenameError(None)
    if not _is_valid_filename(output.stem):
        raise InvalidFilenameError(output.stem)

    if output.suffix is None:
        raise InvalidFileExtensionError(None, None)

    if command is CommandName.GIF:
        if output.suffix != GIF_EXTENSION:
            raise InvalidFileExtensionError(output.suffix, GIF_EXTENSION)
    else:
        if output.suffix not in VIDEO_EXTENSIONS:
            raise InvalidFileExtensionError(output.suffix, VIDEO_EXTENSIONS)

        if target_codec is None:
            raise MissingMediaPropertyError("Video codec")

        valid_containers = CONTAINERS_BY_CODEC.get(target_codec, set())
        if valid_containers and output.suffix not in valid_containers:
            raise InvalidFileExtensionError(output.suffix, valid_containers)

    return output
