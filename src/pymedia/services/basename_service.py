import re
from pathlib import Path

from pymedia.data import CONTAINERS_BY_CODEC, GIF_EXTENSION, VIDEO_EXTENSIONS
from pymedia.models.errors import (
    InvalidFileExtensionError,
    InvalidFilenameError,
    MissingMediaError,
    MissingMediaPropertyError,
)
from pymedia.models.state import State


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


def process_output(state: State, output: Path) -> Path:
    """Comprueba el fichero de salida tenga un nombre y extensión válido."""
    if output.stem is None:
        raise InvalidFilenameError(None)
    if not _is_valid_filename(output.stem):
        raise InvalidFilenameError(output.stem)

    if output.suffix is None:
        raise InvalidFileExtensionError(None, None)

    if state.gif_pipeline is not None:
        if output.suffix != ".gif":
            raise InvalidFileExtensionError(output.suffix, GIF_EXTENSION)

    if output.suffix not in VIDEO_EXTENSIONS:
        raise InvalidFileExtensionError(output.suffix, VIDEO_EXTENSIONS)

    pipeline = state.video_pipeline
    if pipeline is not None and pipeline.requires_encode:
        target_video_codec = state.config.encode.video_codec
    else:
        if not state.media:
            raise MissingMediaError("No se ha podido cargar la información del vídeo.")
        video = state.media[0].video
        if video is None:
            raise MissingMediaPropertyError(
                f"El vídeo '{state.media[0].path}' no tiene stream de vídeo."
            )
        target_video_codec = video.codec

    valid_containers = CONTAINERS_BY_CODEC.get(target_video_codec, set())
    if valid_containers and output.suffix not in valid_containers:
        raise InvalidFileExtensionError(output.suffix, valid_containers)

    return output
