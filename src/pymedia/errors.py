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
        logger.error(self.message)


class CommandError(PyMediaError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class CommandGenerationError(PyMediaError):
    def __init__(self, name: str) -> None:
        super().__init__(
            _("FFmpeg command was not generated: %(name)s ") % {"name": name}
        )


class ConfigError(PyMediaError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class ExclusiveOptionsError(PyMediaError):
    """Excepción para opciones de CLI incompatibles entre sí."""

    def __init__(
        self,
        options: list[str] | None = None,
        option: str | None = None,
        incompatible_with: list[str] | None = None,
    ):
        if options is not None:
            opts_str = ", ".join(f"'{opt}'" for opt in options)
            message = f"The following options are mutually exclusive: {opts_str}."
        elif option is not None and incompatible_with is not None:
            opts_str = ", ".join(f"'{opt}'" for opt in incompatible_with)
            message = f"Option '{option}' cannot be used with: {opts_str}."
        else:
            message = "Incompatible command line options specified."

        super().__init__(message)


class InvalidArgumentError(PyMediaError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class InvalidContainerError(PyMediaError):
    def __init__(self, extension: str, codec: str, supported: str) -> None:
        super().__init__(
            _(
                "Invalid extension %(extension)s. Codec %(codec)s requires one of: "
                "%(supported)s."
            )
            % {"extension": extension, "codec": codec, "supported": supported}
        )


class InvalidContainerTypeError(PyMediaError):
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


class InvalidParameterError(PyMediaError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class InvalidTimeFormatError(PyMediaError):
    def __init__(self) -> None:
        super().__init__(_("Invalid timestamp format. Expected: hh:mm:ss."))


class MissingMediaError(PyMediaError):
    def __init__(self, path: str) -> None:
        super().__init__(_("Missing media information: %(path)s") % {"path": path})


class MissingMediaPropertyError(PyMediaError):
    def __init__(self, name: str) -> None:
        super().__init__(_("Missing media property: %(name)s") % {"name": name})


class MissingParameterError(PyMediaError):
    def __init__(self, name: str) -> None:
        super().__init__(_("Missing parameter: %(name)s") % {"name": name})


class MissingRequiredOptionError(PyMediaError):
    def __init__(self, options: list[str]) -> None:
        super().__init__(
            _("One of the following options is required: %(options)s")
            % {"options": ", ".join(options)}
        )


class OptionError(PyMediaError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)


class PermissionDeniedError(PyMediaError):
    def __init__(self, msg: str) -> None:
        super().__init__(msg)
