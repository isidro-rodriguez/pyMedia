from pymedia import locales
from pymedia.logger import get_logger

logger = get_logger("errors")


class PyMediaError(Exception):
    """
    Base de todos los errores de pyMedia.

    Cada subclase define:
    - `level`: nivel de logging ("ERROR" | "CRITICAL")
    - `category`: diccionario de plantillas en en.py
    - `message_key`: clave de la plantilla a usar

    El mensaje se formatea desde `locales/*.py` y se
    registra automáticamente en el log al levantarse la excepción.
    """

    level = "ERROR"
    category = ""
    message_key = ""

    def __init__(self, **kwargs) -> None:
        """Inicializa el sistema de locales para errores."""
        templates = {
            "ValidationError": locales.ValidationError,
            "PipelineError": locales.PipelineError,
            "ExecutionError": locales.ExecutionError,
        }[self.category]

        self.message = templates[self.message_key].format(**kwargs)
        super().__init__(self.message)

        log_method = logger.critical if self.level == "CRITICAL" else logger.error
        log_method(self.message)


# ─────────────────────────────────────────────────────────────────────────────
#  ExecutionError (nivel CRITICAL)
# ─────────────────────────────────────────────────────────────────────────────


class ExecutionError(PyMediaError):
    """Errores de ejecución. Implican salida de la aplicación."""

    category = "ExecutionError"
    level = "CRITICAL"


class CannotCreateDirectoryError(ExecutionError):
    message_key = "cannot_create_directory"

    def __init__(self, path: str):
        super().__init__(path=path)


class CommandExecutionError(ExecutionError):
    message_key = "command_execution"

    def __init__(self, command_name: str, error: str):
        super().__init__(command_name=command_name, error=error)


class CommandGenerationError(ExecutionError):
    message_key = "command_generation"

    def __init__(self, command_name: str):
        super().__init__(command_name=command_name)


class FFmpegTimeoutError(ExecutionError):
    message_key = "ffmpeg_timeout"


class InvalidConfigError(ExecutionError):
    message_key = "invalid_config"

    def __init__(self, message: str):
        super().__init__(message=message)


# ─────────────────────────────────────────────────────────────────────────────
#  PipelineError
# ─────────────────────────────────────────────────────────────────────────────


class PipelineError(PyMediaError):
    """Errores del pipeline de procesamiento de vídeo."""

    category = "PipelineError"


class IncompatibleFilesError(PipelineError):
    message_key = "incompatible_files"


class MissingArgumentError(PipelineError):
    message_key = "missing_argument"

    def __init__(self, argument: str):
        super().__init__(argument=argument)


class MissingArgumentsError(PipelineError):
    message_key = "missing_arguments"


class MissingMediaError(PipelineError):
    message_key = "missing_media"

    def __init__(self, path: str):
        super().__init__(path=path)


class MissingMediaPropertyError(PipelineError):
    message_key = "missing_media_property"

    def __init__(self, property_name: str):
        super().__init__(property_name=property_name)


class OutputOnConflictError(PipelineError):
    message_key = "output_on_conflict"


# ─────────────────────────────────────────────────────────────────────────────
#  ValidationError
# ─────────────────────────────────────────────────────────────────────────────


class ValidationError(PyMediaError):
    """Errores de validación de la entrada del usuario."""

    category = "ValidationError"


class CropAllZeroError(ValidationError):
    message_key = "crop_all_zero"


class CropExceedsDimensionsError(ValidationError):
    message_key = "crop_exceeds_dimensions"

    def __init__(self, crop_dimensions: str, video_dimensions: str):
        super().__init__(
            crop_dimensions=crop_dimensions, video_dimensions=video_dimensions
        )


class InsufficientInputError(ValidationError):
    message_key = "insufficient_inputs"


class InvalidCropFormatError(ValidationError):
    message_key = "invalid_crop_format"


class InvalidDirectoryError(ValidationError):
    message_key = "invalid_directory_name"

    def __init__(self, directory: str):
        super().__init__(directory=directory)


class InvalidNameError(ValidationError):
    message_key = "invalid_filename"

    def __init__(self, filename: str):
        super().__init__(filename=filename)


class InvalidFileExtensionError(ValidationError):
    message_key = "invalid_extension"

    def __init__(self, extension: str, codec: str, supported: str):
        super().__init__(extension=extension, codec=codec, supported=supported)


class InvalidOutputExtensionError(ValidationError):
    message_key = (
        "invalid_output_extension"  # ver nota abajo: corregir el typo en en.py
    )

    def __init__(self, extension: str, supported: str):
        super().__init__(extension=extension, supported=supported)


class InvalidGyrateError(ValidationError):
    message_key = "invalid_gyrate"


class InvalidSettingError(ValidationError):
    message_key = "invalid_setting"

    def __init__(self, parameter: str):
        super().__init__(parameter=parameter)


class InvalidTimeFormatError(ValidationError):
    message_key = "invalid_time_format"


class InvalidTrimPointsError(ValidationError):
    message_key = "invalid_trim_points"


class MissingOptionsError(ValidationError):
    message_key = "missing_options"


class NegativeTimeError(ValidationError):
    message_key = "negative_time"


class TimeExceedsDurationError(ValidationError):
    message_key = "time_exceeds_duration"

    def __init__(self, time: str, duration: str):
        super().__init__(time=time, duration=duration)
