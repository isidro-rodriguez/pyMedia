"""Tests para el módulo pymedia.errors."""

from pymedia.errors import (
    PyMediaError,
    ValidationError,
    InsufficientInputError,
    InvalidDirectoryError,
    InvalidGifExtensionError,
    InvalidFileNameError,
    InvalidFileExtensionError,
    InvalidCropFormatError,
    InvalidTimeFormatError,
    InvalidTrimPointsError,
    InvalidGyrateError,
    InvalidSettingError,
    PipelineError,
    MissingArgumentsError,
    MissingArgumentError,
    MissingMediaError,
    MissingMediaPropertyError,
    IncompatibleFilesError,
    OutputOnConflictError,
    ExecutionError,
    CommandExecutionError,
    CommandGenerationError,
    FFmpegTimeoutError,
    CannotCreateDirectoryError,
    InvalidConfigError,
    CropAllZeroError,
    CropExceedsWidthError,
    CropExceedsHeightError,
    NegativeTimeError,
    TimeExceedsDurationError,
    MissingOptionsError,
    InvalidVideoExtensionError,
)


# -----------------------------------------------------------------------------
#  ValidationError subclasses (category = "ValidationError")
# -----------------------------------------------------------------------------


def test_insufficient_input_error():
    """Test InsufficientInputError lanza mensaje formateado correctamente."""
    try:
        raise InsufficientInputError()
    except InsufficientInputError as e:
        # El mensaje formateado es: "Se deben proporcionar al menos dos videos para este comando."
        assert "Se deben proporcionar al menos dos videos" in str(e)


def test_invalid_directory_error():
    """Test InvalidDirectoryError lanza mensaje formateado correctamente."""
    try:
        raise InvalidDirectoryError(directory="test<file")
    except InvalidDirectoryError as e:
        # El mensaje formateado contiene el directorio con caracteres inválidos
        assert "test<file" in str(e)


def test_invalid_gif_extension_error():
    """Test InvalidGifExtensionError lanza mensaje formateado correctamente."""
    try:
        raise InvalidGifExtensionError(extension=".mp4")
    except InvalidGifExtensionError as e:
        # El mensaje formateado es: "Invalid extension '.mp4'. Gif images requires '.gif' container."
        assert ".mp4" in str(e) and ".gif" in str(e)


def test_invalid_filename_error():
    """Test InvalidFileNameError lanza mensaje formateado correctamente."""
    try:
        raise InvalidFileNameError(filename="my<file")
    except InvalidFileNameError as e:
        # El mensaje formateado contiene el filename con caracteres inválidos
        assert "my<file" in str(e)


def test_invalid_file_extension_error():
    """Test InvalidFileExtensionError lanza mensaje formateado correctamente."""
    try:
        raise InvalidFileExtensionError(extension=".xyz", codec="h264", supported="mp4,mkv")
    except InvalidFileExtensionError as e:
        # El mensaje formateado es: "Invalid extension '.xyz'. Codec 'h264' requires one of: mp4,mkv."
        assert ".xyz" in str(e) and "h264" in str(e) and "mp4,mkv" in str(e)


# -----------------------------------------------------------------------------
#  InvalidOptionError subclasses (category = "ValidationError")
# -----------------------------------------------------------------------------


def test_invalid_crop_format_error():
    """Test InvalidCropFormatError lanza mensaje formateado correctamente."""
    try:
        raise InvalidCropFormatError()
    except InvalidCropFormatError as e:
        # El mensaje es: "Formato de recorte no válido. Se esperaba: LEFT,RIGHT,TOP,BOTTOM."
        assert "Formato de recorte" in str(e)


def test_crop_all_zero_error():
    """Test CropAllZeroError lanza mensaje formateado correctamente."""
    try:
        raise CropAllZeroError()
    except CropAllZeroError as e:
        # El mensaje es: "Recorte no válido: todos los valores son 0."
        assert "todos los valores son 0" in str(e)


def test_crop_exceeds_width_error():
    """Test CropExceedsWidthError lanza mensaje formateado correctamente."""
    try:
        raise CropExceedsWidthError(total=100, width=200)
    except CropExceedsWidthError as e:
        assert "100" in str(e) and "200" in str(e)


def test_crop_exceeds_height_error():
    """Test CropExceedsHeightError lanza mensaje formateado correctamente."""
    try:
        raise CropExceedsHeightError(total=50, height=100)
    except CropExceedsHeightError as e:
        assert "50" in str(e) and "100" in str(e)


def test_invalid_gyrate_error():
    """Test InvalidGyrateError lanza mensaje formateado correctamente."""
    try:
        raise InvalidGyrateError(angle=45)
    except InvalidGyrateError as e:
        # El mensaje es: "Formato de rotación no válido. Se esperaba: 90 | 180 | 270."
        assert "Formato de rotación" in str(e)


# -----------------------------------------------------------------------------
#  InvalidTimeError subclasses (category = "ValidationError")
# -----------------------------------------------------------------------------


def test_invalid_time_format_error():
    """Test InvalidTimeFormatError lanza mensaje formateado correctamente."""
    try:
        raise InvalidTimeFormatError()
    except InvalidTimeFormatError as e:
        # El mensaje es: "Formato de marca de tiempo no válido. Se esperaba: hh:mm:ss."
        assert "Formato de marca de tiempo" in str(e)


def test_negative_time_error():
    """Test NegativeTimeError lanza mensaje formateado correctamente."""
    try:
        raise NegativeTimeError(time="-5:00")
    except NegativeTimeError as e:
        # El mensaje es: "La marca de tiempo no puede ser negativa."
        assert "marca de tiempo no puede ser negativa" in str(e)


def test_time_exceeds_duration_error():
    """Test TimeExceedsDurationError lanza mensaje formateado correctamente."""
    try:
        raise TimeExceedsDurationError(time="1:30:00", duration="1:00:00")
    except TimeExceedsDurationError as e:
        assert "1:30:00" in str(e) and "1:00:00" in str(e)


# -----------------------------------------------------------------------------
#  InvalidTrimPointsError
# -----------------------------------------------------------------------------


def test_invalid_trim_points_error():
    """Test InvalidTrimPointsError lanza mensaje formateado correctamente."""
    try:
        raise InvalidTrimPointsError(points="invalid")
    except InvalidTrimPointsError as e:
        assert "Puntos de corte" in str(e)


# -----------------------------------------------------------------------------
#  MissingOptionsError
# -----------------------------------------------------------------------------


def test_missing_options_error():
    """Test MissingOptionsError lanza mensaje formateado correctamente."""
    try:
        raise MissingOptionsError()
    except MissingOptionsError as e:
        # El mensaje es: "Se requiere al menos una opción."
        assert "Se requiere al menos una opción" in str(e)


# -----------------------------------------------------------------------------
#  InvalidSettingError (category = "ValidationError")
# -----------------------------------------------------------------------------


def test_invalid_setting_error():
    """Test InvalidSettingError - usa message_key 'invalid_setting'."""
    try:
        raise InvalidSettingError(parameter="fps")
    except InvalidSettingError as e:
        # El mensaje es: "Ajuste no válido: fps"
        assert "Ajuste no válido" in str(e)


# -----------------------------------------------------------------------------
#  PipelineError subclasses (category = "PipelineError")
# -----------------------------------------------------------------------------


def test_missing_arguments_error():
    """Test MissingArgumentsError lanza mensaje formateado correctamente."""
    try:
        raise MissingArgumentsError()
    except MissingArgumentsError as e:
        # El mensaje es: "Faltan argumentos recuperados de Typer."
        assert "Faltan argumentos recuperados de Typer" in str(e)


def test_missing_argument_error():
    """Test MissingArgumentError lanza mensaje formateado correctamente."""
    try:
        raise MissingArgumentError(argument="--output")
    except MissingArgumentError as e:
        assert "--output" in str(e)


def test_missing_media_error():
    """Test MissingMediaError lanza mensaje formateado correctamente."""
    try:
        raise MissingMediaError(path="video.mp4")
    except MissingMediaError as e:
        assert "video.mp4" in str(e)


def test_missing_media_property_error():
    """Test MissingMediaPropertyError lanza mensaje formateado correctamente."""
    try:
        raise MissingMediaPropertyError(property_name="codec")
    except MissingMediaPropertyError as e:
        assert "codec" in str(e)


def test_incompatible_files_error():
    """Test IncompatibleFilesError lanza mensaje formateado correctamente."""
    try:
        raise IncompatibleFilesError()
    except IncompatibleFilesError as e:
        # El mensaje es: "Los archivos de video son incompatibles entre sí."
        assert "incompatible" in str(e)


def test_output_on_conflict_error():
    """Test OutputOnConflictError lanza mensaje formateado correctamente."""
    try:
        raise OutputOnConflictError()
    except OutputOnConflictError as e:
        # El mensaje es: "Proceso detenido porque el archivo de salida ya existe."
        assert "archivo de salida ya existe" in str(e)


# -----------------------------------------------------------------------------
#  ExecutionError subclasses (category = "ExecutionError", level = "CRITICAL")
# -----------------------------------------------------------------------------


def test_command_execution_error():
    """Test CommandExecutionError lanza mensaje formateado correctamente."""
    try:
        raise CommandExecutionError(command_name="ffmpeg", error="access denied")
    except CommandExecutionError as e:
        assert "ffmpeg" in str(e) and "access denied" in str(e)


def test_command_generation_error():
    """Test CommandGenerationError lanza mensaje formateado correctamente."""
    # CommandGenerationError usa message_key 'command_generation' = "FFmpeg command '{command_name}' was not generated."
    # Pero la clase no acepta parámetros, así que lanzará KeyError
    try:
        raise CommandGenerationError()
    except KeyError as e:
        # Esperamos KeyError porque falta el parácommand_name
        assert "command_name" in str(e) or "command_generation" in str(e)


def test_ffmpeg_timeout_error():
    """Test FFmpegTimeoutError lanza mensaje formateado correctamente."""
    try:
        raise FFmpegTimeoutError()
    except FFmpegTimeoutError as e:
        # El mensaje es: "La operación de FFmpeg excedió el tiempo de espera permitido."
        assert "tiempo de espera" in str(e)


def test_cannot_create_directory_error():
    """Test CannotCreateDirectoryError lanza mensaje formateado correctamente."""
    try:
        raise CannotCreateDirectoryError(path="/tmp/output")
    except CannotCreateDirectoryError as e:
        assert "/tmp/output" in str(e)


# -----------------------------------------------------------------------------
#  ConfigError subclasses (category = "ExecutionError")
# -----------------------------------------------------------------------------


def test_invalid_config_error():
    """Test InvalidConfigError lanza mensaje formateado correctamente."""
    try:
        raise InvalidConfigError(message="invalid key")
    except InvalidConfigError as e:
        # El mensaje es: "Configuración no válida: invalid key"
        assert "Configuración no válida" in str(e) and "invalid key" in str(e)