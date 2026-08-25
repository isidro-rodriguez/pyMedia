from pymedia import locales
from pymedia.logger import Logger

logger = Logger.load(__name__)


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

    category = ""
    level = ""
    message_key = ""

    TEMPLATES = {
        "ExecutionError": locales.ExecutionError,
        "ParameterError": locales.ParameterError,
        "ValidationError": locales.ValidationError,
    }

    def __init__(self, **kwargs) -> None:
        """Inicializa el sistema de locales para errores."""

        self.message = self.TEMPLATES[self.category][self.message_key].format(**kwargs)
        super().__init__(self.message)

        if self.level == "CRITICAL":
            logger.critical(self.message)
        else:
            logger.error(self.message)


# ─────────────────────────────────────────────────────────────────────────────
#  Errores de ejecución (Errores críticos)
# ─────────────────────────────────────────────────────────────────────────────


class ExecutionError(PyMediaError):
    """Errores de ejecución. Implican salida de la aplicación."""

    category = "ExecutionError"
    level = "CRITICAL"


class CannotCreateDirectoryError(ExecutionError):
    message_key = "cannot_create_directory"

    def __init__(self, path: str) -> None:
        super().__init__(path=path)


class CommandExecutionError(ExecutionError):
    message_key = "command_execution"

    def __init__(self, command_name: str, error: str) -> None:
        super().__init__(command_name=command_name, error=error)


class CommandGenerationError(ExecutionError):
    message_key = "command_generation"

    def __init__(self, command_name: str) -> None:
        super().__init__(command_name=command_name)


class CommandTimeoutError(ExecutionError):
    message_key = "command_timeout"

    def __init__(self, command_name: str) -> None:
        super().__init__(command_name=command_name)


class InvalidConfigError(ExecutionError):
    message_key = "invalid_config"

    def __init__(self, message: str) -> None:
        super().__init__(message=message)


# ─────────────────────────────────────────────────────────────────────────────
#  Errores en el proceso de parámetros
# ─────────────────────────────────────────────────────────────────────────────


class ParameterError(PyMediaError):
    """Errores del pipeline de procesamiento de vídeo."""

    category = "ParameterError"
    level = "ERROR"


class ConflictiveOutputParametersError(ParameterError):
    message_key = "conflictive_output_parameters"


class ConflictiveResizeDimensionsParametersError(ParameterError):
    message_key = "conflictive_resize_dimensions_parameters"


class MissingArgumentError(ParameterError):
    message_key = "missing_argument"

    def __init__(self, argument: str) -> None:
        super().__init__(argument=argument)


class MissingMediaError(ParameterError):
    message_key = "missing_media"

    def __init__(self, path: str) -> None:
        super().__init__(path=path)


class MissingMediaPropertyError(ParameterError):
    message_key = "missing_media_property"

    def __init__(self, property_name: str) -> None:
        super().__init__(property_name=property_name)


class MissingParameterError(ParameterError):
    message_key = "missing_parameter"

    def __init__(self, parameter: str) -> None:
        super().__init__(parameter=parameter)


class OutputParameterError(ParameterError):
    message_key = "output_parameter"


# ─────────────────────────────────────────────────────────────────────────────
#  Errores de validación
# ─────────────────────────────────────────────────────────────────────────────


class ValidationError(PyMediaError):
    """Errores de validación de la entrada del usuario."""

    category = "ValidationError"
    level = "ERROR"


class CropExceedsDimensionsError(ValidationError):
    message_key = "crop_exceeds_dimensions"

    def __init__(self, crop_dimensions: str, video_dimensions: str) -> None:
        super().__init__(
            crop_dimensions=crop_dimensions, video_dimensions=video_dimensions
        )


class InvalidBordersFormatError(ValidationError):
    message_key = "invalid_borders_format"


class InvalidCropFormatError(ValidationError):
    message_key = "invalid_crop_format"


class InvalidDirectoryError(ValidationError):
    message_key = "invalid_directory_name"

    def __init__(self, directory: str) -> None:
        super().__init__(directory=directory)


class InvalidNameError(ValidationError):
    message_key = "invalid_filename"

    def __init__(self, filename: str) -> None:
        super().__init__(filename=filename)


class InvalidFileExtensionError(ValidationError):
    message_key = "invalid_extension"

    def __init__(self, extension: str, codec: str, supported: str) -> None:
        super().__init__(extension=extension, codec=codec, supported=supported)


class InvalidContainerTypeError(ValidationError):
    message_key = "invalid_container_type"

    def __init__(self, extension: str, media_type: str, supported: str) -> None:
        super().__init__(
            extension=extension, media_type=media_type.capitalize(), supported=supported
        )


class InvalidTimeFormatError(ValidationError):
    message_key = "invalid_time_format"


class TimeExceedsDurationError(ValidationError):
    message_key = "time_exceeds_duration"

    def __init__(self, time: str, duration: str) -> None:
        super().__init__(time=time, duration=duration)
