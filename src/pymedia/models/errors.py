class MissingMediaError(ValueError):
    """No se puede obtener información del vídeo."""


class MissingMediaPropertyError(MissingMediaError):
    """No se puede obtener la propiedad del vídeo."""


class MissingOptionsError(ValueError):
    """Valor de opcion inválido."""


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


class InvalidOptionError(PipelineValidationError):
    """Valor de opción inválido."""
