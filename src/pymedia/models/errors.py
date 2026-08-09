from path import Path


class CommandExecutionError(Exception):
    """Raised when a command fails during execution."""

    def __init__(self, command_name: str, error: str) -> None:
        message = (
            f"FFmpeg command '{command_name}' failed during execution. Error: {error}"
        )

        super().__init__(message)


class CommandGenerationError(Exception):
    """Raised when an FFmpeg command cannot be generated."""

    def __init__(self, command_name: str) -> None:
        message = f"FFmpeg command '{command_name}' was not generated."

        super().__init__(message)


class FFmpegTimeoutError(Exception):
    """Raised when an FFmpeg operation exceeds the allowed timeout."""


class IncompatibleFilesError(Exception):
    """Raised when files are incompatible with each other."""

    def __init__(self) -> None:
        message = "Video files are incompatible with each other."

        super().__init__(message)


class InsufficientInputError(Exception):
    """Raised when the number of inputs is below the required minimum."""

    def __init__(self) -> None:
        message = "Se requieren al menos proporcionar dos vídeos para este comando."

        super().__init__(message)


class InvalidFilenameError(ValueError):
    """Excepción levantada cuando el nombre del fichero no sea válido."""

    def __init__(self, filename: str | None) -> None:
        if filename is None:
            message = "Se requiere especificar un nombre de fichero."
        else:
            message = (
                f"'{filename}' contiene caracteres no válidos: '< > : \" / \\ | ? *'"
            )
        super().__init__(message)


class InvalidFileExtensionError(ValueError):
    """Excepción levantada cuando una extensión no soporta el contenido multimedia."""

    def __init__(
        self, extension: str | None, supported_extensions: list[str] | str | None
    ) -> None:
        if extension is None:
            message = "Se requiere especificar una extensión."
        else:
            self.extension = extension
            self.supported_extensions = supported_extensions
            if supported_extensions is None:
                message = f"Extensión '{extension}' no válida."
            else:
                message = (
                    f"Extensión '{extension}' no válida. "
                    f"Tiene que ser: {', '.join(sorted(supported_extensions))}"
                )
        super().__init__(message)


class InvalidTrimPointsError(ValueError):
    """Excepción levantada cuando las marcas de tiempo para corte son inválidas."""

    pass


class PipelineValidationError(ValueError):
    """Error base de validación del pipeline."""

    pass


class InvalidOptionError(PipelineValidationError):
    """Valor de opción inválido."""

    pass


class InvalidPropertyValueError(Exception):
    """Raised when a property has an invalid value for its operation."""

    def __init__(self, prop: str, operation: str) -> None:
        message = f"Property '{prop}' has an invalid value for {operation}."

        super().__init__(message)


class MissingMediaError(ValueError):
    """Raised when multimedia video information could not be found."""

    def __init__(self, path: Path) -> None:
        message = f"Media information of '{path}' could not be found."

        super().__init__(message)


class MissingMediaPropertyError(MissingMediaError):
    """No se puede obtener la propiedad del vídeo."""

    def __init__(self, property_name: str) -> None:
        message = f"'{property_name}' media information could not be found."

        super().__init__(message)


class MissingOptionsError(ValueError):
    """Valor de opcion inválido."""

    pass


class ValueComparisonError(Exception):
    """Raised when values cannot be compared."""

    def __init__(self, command: str, value: str) -> None:
        message = f"'{value}' values cannot be compared for '{command}'."

        super().__init__(message)
