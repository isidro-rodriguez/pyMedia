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
#  ValidationError (nivel ERROR)
# ─────────────────────────────────────────────────────────────────────────────


class ValidationError(PyMediaError):
    """Errores de validación de la entrada del usuario."""

    category = "ValidationError"


class InsufficientInputError(ValidationError):
    message_key = "insufficient_inputs"


class InvalidPathError(ValidationError):
    """Errores de validación de rutas de archivo."""


class InvalidDirectoryError(InvalidPathError):
    message_key = "invalid_directory_name"


class InvalidFileNameError(InvalidPathError):
    message_key = "invalid_filename"


class InvalidFileExtensionError(InvalidPathError):
    message_key = "invalid_extension"


class InvalidOptionError(ValidationError):
    """Base de errores de opciones CLI inválidas."""


class InvalidCropError(InvalidOptionError):
    """Errores de la opción --crop."""


class InvalidCropFormatError(InvalidCropError):
    message_key = "invalid_crop_format"


class CropAllZeroError(InvalidCropError):
    message_key = "crop_all_zero"


class CropExceedsWidthError(InvalidCropError):
    message_key = "crop_exceeds_width"


class CropExceedsHeightError(InvalidCropError):
    message_key = "crop_exceeds_height"


class InvalidGyrateError(InvalidOptionError):
    message_key = "invalid_gyrate"


class InvalidTimeError(InvalidOptionError):
    """Errores de marcas de tiempo."""


class InvalidTimeFormatError(InvalidTimeError):
    message_key = "invalid_time_format"


class NegativeTimeError(InvalidTimeError):
    message_key = "negative_time"


class TimeExceedsDurationError(InvalidTimeError):
    message_key = "time_exceeds_duration"


class InvalidTrimPointsError(ValidationError):
    message_key = "invalid_trim_points"


class MissingOptionsError(ValidationError):
    message_key = "missing_options"


class InvalidSettingError(ValidationError):
    message_key = "invalid_setting"


# ─────────────────────────────────────────────────────────────────────────────
#  PipelineError (nivel ERROR)
# ─────────────────────────────────────────────────────────────────────────────


class PipelineError(PyMediaError):
    """Errores del pipeline de procesamiento de vídeo."""

    category = "PipelineError"


class ArgumentError(PipelineError):
    """Errores relacionados con los argumentos recogidos por Typer."""


class MissingArgumentsError(ArgumentError):
    message_key = "missing_arguments"


class MissingArgumentError(ArgumentError):
    message_key = "missing_argument"


class MediaError(PipelineError):
    """Errores relacionados con los datos del medio (ffprobe)."""


class MissingMediaError(MediaError):
    message_key = "missing_media"


class MissingMediaPropertyError(MediaError):
    message_key = "missing_media_property"


class IncompatibleFilesError(PipelineError):
    message_key = "incompatible_files"


class OutputOnConflictError(PipelineError):
    message_key = "output_on_conflict"


# ─────────────────────────────────────────────────────────────────────────────
#  ExecutionError (nivel CRITICAL)
# ─────────────────────────────────────────────────────────────────────────────


class ExecutionError(PyMediaError):
    """Errores de ejecución. Implican salida de la aplicación."""

    category = "ExecutionError"
    level = "CRITICAL"


class CommandExecutionError(ExecutionError):
    message_key = "command_execution"


class CommandGenerationError(ExecutionError):
    message_key = "command_generation"


class FFmpegTimeoutError(ExecutionError):
    message_key = "ffmpeg_timeout"


class CannotCreateDirectoryError(ExecutionError):
    message_key = "cannot_create_directory"


class ConfigError(ExecutionError):
    """Errores relacionados con el fichero de configuración."""


class InvalidConfigError(ConfigError):
    message_key = "invalid_config"
