import re
import subprocess
from datetime import timedelta
from json import JSONDecodeError
from pathlib import Path

from pymedia.data.audio_codecs import AUDIO_CODECS
from pymedia.data.containers import VIDEO_CONTAINERS
from pymedia.data.video_codecs import VIDEO_CODECS
from pymedia.errors import (
    CannotCreateDirectoryError,
    CropExceedsDimensionsError,
    InvalidCropFormatError,
    InvalidDirectoryError,
    InvalidFileExtensionError,
    InvalidNameError,
    InvalidOutputExtensionError,
    InvalidTimeFormatError,
    MissingMediaError,
    MissingMediaPropertyError,
    TimeExceedsDurationError,
)
from pymedia.logger import get_logger, log_warning
from pymedia.models.base_parameters import (
    CommandMode,
    CropMargins,
    ScaleModeT,
)
from pymedia.models.config import Config
from pymedia.models.media import Media

logger = get_logger("parameters")


def load_media(
    paths: list[Path],
) -> list[Media]:
    """
    Carga la lista de metadatos de los vídeos a procesar

    Args:
        paths: rutas absolutas de los vídeos

    Returns:
        Lista de metadatos

    Raises:
        MissingMediaError: Si no se pueden obtener metadatos del vídeo.
    """

    def _validate_video_extension() -> None:
        """Valida que la lista de ficheros tengan extensiones de vídeos."""
        for path in paths:
            if path.suffix is None:
                raise InvalidOutputExtensionError(
                    extension="None",
                    supported=", ".join(VIDEO_CONTAINERS),
                )
            if path.suffix not in VIDEO_CONTAINERS:
                raise InvalidOutputExtensionError(
                    extension=path.suffix,
                    supported=", ".join(VIDEO_CONTAINERS),
                )

    _validate_video_extension()

    media: list[Media] = []

    for p in paths:
        try:
            m: Media = Media.load(p)
        except (
            ValueError,
            subprocess.CalledProcessError,
            JSONDecodeError,
            OSError,
        ) as e:
            raise MissingMediaError(path=str(p)) from e

        media.append(m)

    return media


def process_crop(
    crop: str | None,
    media: list[Media],
    dimensions: list[tuple[int, int]] | None = None,
) -> list[CropMargins]:
    """
    Procesa la opción de corte de imagen.

    Args:
        crop: Valor de las dimensiones de corte.
        media: Metadatos de los vídeos a procesar.
        dimensions: Dimensiones normalizadas para CONCAT incompatible.

    Returns:
        Lista de las dimensiones de corte.

    Raises:
        CropExceedsDimensionsError: Si el corte excede el vídeo original.
        InvalidCropFormatError: Si el formato no es parseable.
        MissingMediaPropertyError: Si falta metadata necesaria en `media`.
    """

    crop_list: list[CropMargins] = []

    def _validate_crop(values_str: str) -> None:
        """Valida el formato y los valores del corte."""
        try:
            values = tuple(int(v) for v in values_str.split(","))
        except ValueError as exc:
            raise InvalidCropFormatError() from exc
        if (
            not len(values) == 4
            or not all(v >= 0 for v in values)
            or not max(values) > 0
        ):
            raise InvalidCropFormatError()

    def _validate_crop_dimensions() -> None:
        """Valida que las dimensiones de corte no igualen o excedan a las del vídeo."""
        if width <= left + right or height <= top + bottom:
            raise CropExceedsDimensionsError(
                crop_dimensions=f"{left + right}x{top + bottom}",
                video_dimensions=f"{width}x{height}",
            )

    def _parse_to_tuple(values: str) -> tuple[int, ...]:
        """Transforma el str validado a tuple con tipos."""
        return tuple(map(int, values.split(",")))

    if crop is None:
        raise InvalidCropFormatError()

    _validate_crop(crop)

    left, right, top, bottom = _parse_to_tuple(crop)

    for i, media_item in enumerate(media):
        if (
            media_item.video is None
            or media_item.video.width is None
            or media_item.video.height is None
        ):
            raise MissingMediaPropertyError(property_name="Crop")

        if dimensions is not None:
            width, height = dimensions[i]
        else:
            width, height = media_item.video.width, media_item.video.height

        _validate_crop_dimensions()

        crop_list.append(
            CropMargins(
                width=width - left - right,
                height=height - top - bottom,
                x=left,
                y=top,
            )
        )

    return crop_list


def process_output(
    output: Path,
    command: CommandMode,
    config: Config,
    media: list[Media],
    requires_audio_transcode: bool = False,
    requires_video_transcode: bool = False,
) -> Path:
    """
    Comprueba el fichero de salida tenga un nombre y extensión válido.

    Args:
        output: Path absoluto del nombre de salida.
        command: Commando ejecutado en la CLI.
        config: Parámetros de configuración de la aplicación.
        media: Lista de metadatos, obtenidos por ffprobe, de los vídeos a procesar.
        requires_audio_transcode: Si los vídeos va a tener el audio transcodificado.
        requires_video_transcode: Si los vídeos va a tener el video transcodificado.

    Returns:
        Path absoluto de salida.

    Raises:
        MissingMediaPropertyError: No se ha podido obtener una propiedad de media.
        InvalidFileExtensionError: Extensión de fichero inválida según el criterio.
        CannotCreateDirectoryError: El usuario no tiene permisos de escritura
                en la ruta aportada.
        InvalidNameError: Nombre de archivo, o directorio, con caracteres inválidos.
        InvalidGifExtensionError: Fichero GIF de salida con extensión incorrecta.
    """

    def _is_valid_name(name: str) -> bool:
        """
        Valida si el nombre de archivo, o directorio,
        no contiene caracteres no permitidos en Windows
        """
        _INVALID_CHARS = re.compile(r'[<>:"/\\|?*\x00-\x1F]')
        _RESERVED_NAMES = {"CON", "PRN", "AUX", "NUL"} | {
            f"{p}{n}" for p in ("COM", "LPT") for n in range(1, 10)
        }
        return bool(
            name
            and not _INVALID_CHARS.search(name)
            and not name.endswith((" ", "."))
            and name.upper().split(".")[0] not in _RESERVED_NAMES
        )

    def _validate_video_codec_container(video_codec: str, video_container: str) -> None:
        """Valida que se utiliza un container adecuado para el códec de vídeo."""
        video_codec_data = VIDEO_CODECS[video_codec]

        if (
            video_codec_data.containers
            and video_container not in video_codec_data.containers
        ):
            raise InvalidFileExtensionError(
                extension=output.suffix,
                codec=video_codec_data.name,
                supported=",".join(video_codec_data.containers),
            )

    def _validate_audio_codec_container(audio_codec: str, audio_container: str) -> None:
        """Valida que se utiliza un container adecuado para el códec de audio."""
        if config.encode.audio_codec is not None:
            audio_codec_data = AUDIO_CODECS[audio_codec]

            if (
                audio_codec_data.containers
                and audio_container not in audio_codec_data.containers
            ):
                raise InvalidFileExtensionError(
                    extension=output.suffix,
                    codec=audio_codec_data.name,
                    supported=",".join(audio_codec_data.containers),
                )

    # Comprobación del directorio (solo si se va a crear/escritura en subdirectorio)
    if output.parent != Path(".") and not _is_valid_name(output.parent.name):
        raise InvalidDirectoryError(directory=output.parent.name)
    try:
        output.parent.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        raise CannotCreateDirectoryError(path=str(output.parent)) from e

    # Comprobación del nombre de fichero
    if output.stem is None:
        raise InvalidNameError(filename="None")
    if not _is_valid_name(output.stem):
        raise InvalidNameError(filename=output.stem)

    # Comprobación de extensión en la generación de GIF
    if command is CommandMode.GIF:
        if output.suffix != ".gif":
            raise InvalidOutputExtensionError(extension=output.suffix, supported=".gif")
        return output

    # Comprobación de que se usa una extensión de vídeo válida
    if output.suffix not in VIDEO_CONTAINERS:
        raise InvalidOutputExtensionError(
            extension=output.suffix,
            supported=",".join(VIDEO_CONTAINERS),
        )

    for m in media:
        # Comprobación de extensión respecto al codec de vídeo utilizado en la
        # transcodificación o respecto al del vídeo origen si no la hubiese.
        if requires_video_transcode:
            if config.encode.video_codec is None:
                raise MissingMediaPropertyError(property_name="Video codec")
            _validate_video_codec_container(
                video_codec=config.encode.video_codec,
                video_container=output.suffix,
            )
        else:
            if m.video is None or m.video.codec is None:
                raise MissingMediaPropertyError(property_name="Video codec")
            _validate_video_codec_container(
                video_codec=m.video.codec,
                video_container=output.suffix,
            )

        # Comprobación de extensión respecto al codec de audio utilizado en la
        # transcodificación o respecto al del vídeo origen si no la hubiese.
        if m.audio is not None:
            if requires_audio_transcode:
                if config.encode.audio_codec is None:
                    raise MissingMediaPropertyError(property_name="Audio codec")
                _validate_audio_codec_container(
                    audio_codec=config.encode.audio_codec,
                    audio_container=output.suffix,
                )
            else:
                if m.audio.codec is None:
                    raise MissingMediaPropertyError(property_name="Audio codec")
                _validate_audio_codec_container(
                    audio_codec=m.audio.codec,
                    audio_container=output.suffix,
                )

    return output


def process_scale(
    scale: ScaleModeT,
    media: list[Media],
    config: Config,
) -> list[ScaleModeT | None]:
    """
    Valida y procesa la opción de escalado.

    Args:
        scale: Valor de las dimensiones de scale.
        media: Metadatos de los vídeos a procesar.
        config: Parámetros de configuración.

    Returns:
        Lista de las dimensiones de escalado.

    Raises:
        MissingMediaPropertyError: Si no se puede obtener la altura del vídeo.

    Warnings:
        scale_rejected_equal: Informa que no se escala si la altura elegida
                coincide con la altura del vídeo.
        scale_rejected_increase: Si está activada la opción en configuración, informa
                que no se escala si la altura elegida es mayor a la altura del vídeo.
    """
    scale_list: list[ScaleModeT | None] = []

    for media_item in media:
        if media_item.video is None or media_item.video.height is None:
            raise MissingMediaPropertyError(property_name="height")

        if scale == media_item.video.height:
            log_warning(
                logger=logger,
                key="scale_rejected_equal",
                scale=scale.value,
                height=media_item.video.height,
            )
            scale_list.append(None)
            continue

        if config.app.disable_resolution_increase and scale > media_item.video.height:
            log_warning(
                logger=logger,
                key="scale_rejected_increase",
                scale=scale.value,
                height=media_item.video.height,
            )
            scale_list.append(None)
            continue

        scale_list.append(scale)

    return scale_list


def process_time(
    time_str: str,
    media: Media,
) -> timedelta:
    """
    Valida y procesa la marca de tiempo.

    Args:
        time_str: Marca de tiempo en formato string.
        media: Metadatos del vídeo a procesar.

    Returns:
        Marca de tiempo en formato timedelta.

    Raises:
        InvalidTimeFormatError: si el formato de la marca no es válido.
        MissingMediaPropertyError: si no se pudo obtener la duración del vídeo.
        TimeExceedsDurationError: si la marca de tiempo es superior
                a la duración del vídeo
    """

    def _parse_to_timedelta() -> timedelta:
        """Convierte str ('hh:mm:ss', 'mm:ss', 'ss') a timedelta."""
        parts = time_str.split(":")
        if not all(p.isdigit() for p in parts):
            raise InvalidTimeFormatError()
        match tuple(map(float, parts)):
            case (hours, minutes, seconds):
                return timedelta(hours=hours, minutes=minutes, seconds=seconds)
            case (minutes, seconds):
                return timedelta(minutes=minutes, seconds=seconds)
            case (seconds,):
                return timedelta(seconds=seconds)
            case _:
                raise InvalidTimeFormatError()

    def _validate_time() -> None:
        """Valida que la marca de tiempo no supere la duración del vídeo."""
        if media.duration is None:
            raise MissingMediaPropertyError(property_name="video.duration")
        if time_delta > media.duration:
            raise TimeExceedsDurationError(
                time=str(time_delta), duration=str(media.duration)
            )

    time_delta = _parse_to_timedelta()
    _validate_time()

    return time_delta


def process_trim_points(
    trim_points_str: str,
    media: Media,
) -> list[timedelta]:
    """
    Valida y procesa una lista de marcas de tiempo.

    Args:
        trim_points_str: Marcas de tiempo en formato string.
        media: Metadatos del vídeo a procesar.

    Returns:
        Lista de marcas de tiempo en formato timedelta.

    Raises:
        InvalidTimeFormatError: Si el formato de alguna de las marcas no es válido.
        MissingMediaPropertyError: Si no se pudo obtener la duración del vídeo.
        TimeExceedsDurationError: Si alguna de las marcas de tiempo es superior
                a la duración del vídeo
    """

    trim_points_timedelta: list[timedelta] = []

    for tp in trim_points_str.split(","):
        trim_points_timedelta.append(process_time(time_str=tp, media=media))

    trim_points_timedelta.sort()

    return trim_points_timedelta
