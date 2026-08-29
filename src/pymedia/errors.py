import logging

from pymedia.locales import _  # noqa
from pymedia.logger import Logger

logger = Logger(logging.getLogger("pymedia.logger"))


class PyMediaError(Exception):
    """Base de todos los errores de pyMedia.

    Cada subclase construye su mensaje con `_("msgid") % kwargs` en el
    momento de lanzarse, de modo que usa el idioma activo del catálogo.
    El mensaje se registra automáticamente en el log.

    Attributes:
        level: Nivel de logging ("ERROR" | "CRITICAL").
    """

    level = ""

    def __init__(self, message: str) -> None:
        self.message = message
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

    level = "CRITICAL"


class CannotCreateDirectoryError(ExecutionError):
    def __init__(self, path: str) -> None:
        super().__init__(_("Could not create directory: %(path)s") % {"path": path})


class CommandExecutionError(ExecutionError):
    def __init__(self, command_name: str, error: str) -> None:
        super().__init__(
            _(
                "FFmpeg command %(command_name)s failed during execution. Error: "
                "%(error)s"
            )
            % {"command_name": command_name, "error": error}
        )


class CommandGenerationError(ExecutionError):
    def __init__(self, command_name: str) -> None:
        super().__init__(
            _("FFmpeg command %(command_name)s was not generated.")
            % {"command_name": command_name}
        )


class CommandTimeoutError(ExecutionError):
    def __init__(self, command_name: str) -> None:
        super().__init__(
            _("FFmpeg command %(command_name)s timed out.")
            % {"command_name": command_name}
        )


class InvalidConfigError(ExecutionError):
    def __init__(self, message: str) -> None:
        super().__init__(_("Invalid configuration: %(message)s") % {"message": message})


# ─────────────────────────────────────────────────────────────────────────────
#  Errores en el proceso de parámetros
# ─────────────────────────────────────────────────────────────────────────────


class ParameterError(PyMediaError):
    """Errores del pipeline de procesamiento de vídeo."""

    level = "ERROR"


class ConflictiveOutputAmmountParameterError(ParameterError):
    def __init__(self) -> None:
        super().__init__(
            _(
                "It is not allowed to specify an output with multiple inputs, "
                "use output directory instead."
            )
        )


class ConflictiveOutputParametersError(ParameterError):
    def __init__(self) -> None:
        super().__init__(
            _("It is not allowed to specify an output path and an output directory.")
        )


class ConflictiveResizeDimensionsParametersError(ParameterError):
    def __init__(self) -> None:
        super().__init__(_("It is not allowed to specify width and height together."))


class MissingArgumentError(ParameterError):
    def __init__(self, argument: str) -> None:
        super().__init__(_("Missing argument: %(argument)s") % {"argument": argument})


class MissingMediaError(ParameterError):
    def __init__(self, path: str) -> None:
        super().__init__(_("Missing media information: %(path)s") % {"path": path})


class MissingMediaPropertyError(ParameterError):
    def __init__(self, name: str) -> None:
        super().__init__(_("Missing media property: %(name)s") % {"name": name})


class MissingParameterError(ParameterError):
    def __init__(self, name: str) -> None:
        super().__init__(_("Missing name: %(name)s") % {"name": name})


class OutputParameterError(ParameterError):
    def __init__(self) -> None:
        super().__init__(
            _(
                "It is not allowed to specify an output if it has been provided "
                "multiple video inputs."
            )
        )


# ─────────────────────────────────────────────────────────────────────────────
#  Errores de validación
# ─────────────────────────────────────────────────────────────────────────────


class ValidationError(PyMediaError):
    """Errores de validación de la entrada del usuario."""

    level = "ERROR"


class CropExceedsDimensionsError(ValidationError):
    def __init__(self, crop_dimensions: str, video_dimensions: str) -> None:
        super().__init__(
            _(
                "Invalid crop dimensions: %(crop_dimensions)s >= original "
                "%(video_dimensions)s."
            )
            % {"crop_dimensions": crop_dimensions, "video_dimensions": video_dimensions}
        )


class InvalidBordersFormatError(ValidationError):
    def __init__(self) -> None:
        super().__init__(_("Invalid borders format. Expected: LEFT,RIGHT,TOP,BOTTOM."))


class InvalidCropFormatError(ValidationError):
    def __init__(self) -> None:
        super().__init__(_("Invalid crop format. Expected: WIDTH,HEIGHT,X,Y."))


class InvalidDirectoryError(ValidationError):
    def __init__(self, directory: str) -> None:
        super().__init__(
            _(r'%(directory)s contains invalid characters: < > : " / \ | ? *')
            % {"directory": directory}
        )


class InvalidNameError(ValidationError):
    def __init__(self, filename: str) -> None:
        super().__init__(
            _(r'%(filename)s contains invalid characters: < > : " / \ | ? *')
            % {"filename": filename}
        )


class InvalidFileExtensionError(ValidationError):
    def __init__(self, extension: str, codec: str, supported: str) -> None:
        super().__init__(
            _(
                "Invalid extension %(extension)s. Codec %(codec)s requires one of: "
                "%(supported)s."
            )
            % {"extension": extension, "codec": codec, "supported": supported}
        )


class InvalidContainerTypeError(ValidationError):
    def __init__(self, extension: str, media_type: str, supported: str) -> None:
        super().__init__(
            _(
                "Invalid extension %(extension)s. %(media_type)s requires one of: "
                "%(supported)s."
            )
            % {
                "extension": extension,
                "media_type": media_type.capitalize(),
                "supported": supported,
            }
        )


class InvalidTimeFormatError(ValidationError):
    def __init__(self) -> None:
        super().__init__(_("Invalid timestamp format. Expected: hh:mm:ss."))


class TimeExceedsDurationError(ValidationError):
    def __init__(self, time: str, duration: str) -> None:
        super().__init__(
            _("Timestamp %(time)s exceeds video duration %(duration)s.")
            % {"time": time, "duration": duration}
        )
