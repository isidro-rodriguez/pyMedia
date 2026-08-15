from pymedia import locales
from pymedia.logger import get_logger

logger = get_logger("errors")


class PyMediaError(Exception):
    """Base de todos los errores de pyMedia.

    Cada subclase define:
    - `level`: nivel de logging ("ERROR" | "CRITICAL")
    - `category`: diccionario de plantillas en en.py
    - `message_key`: clave de la plantilla a usar

    El mensaje se formatea desde `locales/en.py` y se
    registra automáticamente en el log al levantarse la excepción.
    """

    level = "ERROR"
    category = ""
    message_key = ""

    def __init__(self, **kwargs) -> None:
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


class CommandExecutionError(ExecutionError):
    message_key = "command_execution"


class CommandGenerationError(ExecutionError):
    message_key = "command_generation"


class FFmpegTimeoutError(ExecutionError):
    message_key = "ffmpeg_timeout"


class InvalidConfigError(ExecutionError):
    message_key = "invalid_config"


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


class MissingArgumentsError(PipelineError):
    message_key = "missing_arguments"


class MissingMediaError(PipelineError):
    message_key = "missing_media"


class MissingMediaPropertyError(PipelineError):
    message_key = "missing_media_property"


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


class CropExceedsHeightError(ValidationError):
    message_key = "crop_exceeds_height"


class CropExceedsWidthError(ValidationError):
    message_key = "crop_exceeds_width"


class InsufficientInputError(ValidationError):
    message_key = "insufficient_inputs"


class InvalidCropFormatError(ValidationError):
    message_key = "invalid_crop_format"


class InvalidDirectoryError(ValidationError):
    message_key = "invalid_directory_name"


class InvalidFileNameError(ValidationError):
    message_key = "invalid_filename"


class InvalidFileExtensionError(ValidationError):
    message_key = "invalid_extension"


class InvalidGifExtensionError(ValidationError):
    message_key = "invalid_gif_extension"


class InvalidGyrateError(ValidationError):
    message_key = "invalid_gyrate"


class InvalidSettingError(ValidationError):
    message_key = "invalid_setting"


class InvalidTimeFormatError(ValidationError):
    message_key = "invalid_time_format"


class InvalidTrimPointsError(ValidationError):
    message_key = "invalid_trim_points"


class InvalidVideoExtensionError(ValidationError):
    message_key = "invalid_video_extension"


class MissingOptionsError(ValidationError):
    message_key = "missing_options"


class NegativeTimeError(ValidationError):
    message_key = "negative_time"


class TimeExceedsDurationError(ValidationError):
    message_key = "time_exceeds_duration"
