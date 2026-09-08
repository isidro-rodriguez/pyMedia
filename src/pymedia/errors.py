"""Jerarquía de excepciones de pyMedia.

Cada subclase construye su mensaje con `_("msgid") % kwargs` en el momento de
lanzarse, de modo que usa el idioma activo del catálogo. `PyMediaError` registra
automáticamente el mensaje en el log.
"""

import logging

from pymedia.locales import _  # noqa
from pymedia.logger import Logger

logger = Logger(logging.getLogger("pymedia.logger"))


class PyMediaError(Exception):
    """Base de todos los errores de pyMedia.

    Cada subclase construye su mensaje con `_("msgid") % kwargs` en el
    momento de lanzarse, de modo que usa el idioma activo del catálogo.
    El mensaje se registra automáticamente en el log.
    """

    def __init__(self, msg: str) -> None:
        """Inicializa el error y registra el mensaje en el log.

        Args:
            msg: Mensaje de error ya formateado.
        """
        self.msg = msg
        super().__init__(self.msg)
        logger.error(self.msg)


class AudioError(PyMediaError):
    """Error relacionado con la manipulación de pistas de audio."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)


class CommandError(PyMediaError):
    """Error durante la ejecución de un comando ffmpeg."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)


class CommandGenerationError(PyMediaError):
    """Error al intentar construir el comando ffmpeg."""

    def __init__(self, name: str) -> None:
        """Inicializa el error indicando qué comando no se generó.

        Args:
            name: Nombre interno del comando o filtro fallido.
        """
        super().__init__(
            _("FFmpeg command was not generated: %(command_name)s")
            % {"command_name": name}
        )


class ConfigError(PyMediaError):
    """Error de validación de la configuración de la aplicación."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)


class ExclusiveOptionsError(PyMediaError):
    """Excepción para opciones de CLI incompatibles entre sí."""

    def __init__(
        self,
        options: list[str] | None = None,
        option: str | None = None,
        incompatible_with: list[str] | None = None,
    ):
        """Inicializa el error con las opciones en conflicto.

        Args:
            options: Opciones mutuamente excluyentes, si el conflicto es
                de exclusividad general.
            option: Opción que entra en conflicto con otras.
            incompatible_with: Opciones incompatibles con `option`.
        """
        if options is not None:
            opts_str = ", ".join(f"'{opt}'" for opt in options)
            message = f"The following options are mutually exclusive: {opts_str}."
        elif option is not None and incompatible_with is not None:
            opts_str = ", ".join(f"'{opt}'" for opt in incompatible_with)
            message = f"Option '{option}' cannot be used with: {opts_str}."
        else:
            message = "Incompatible command line options specified."

        super().__init__(message)


class FfprobeError(PyMediaError):
    """Errores relacionados con subtítulos."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)


class InvalidArgumentError(PyMediaError):
    """Error por un argumento de CLI con valor no válido."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)


class InvalidContainerError(PyMediaError):
    """Error cuando la extensión no es compatible con el códec usado."""

    def __init__(self, extension: str, codec: str, supported: str) -> None:
        """Inicializa el error con la extensión, el códec y las válidas.

        Args:
            extension: Extensión del fichero de salida.
            codec: Códec usado en la salida.
            supported: Extensiones de contenedor soportadas por el códec.
        """
        super().__init__(
            _(
                "Invalid extension %(extension)s. Codec %(codec)s requires one of: "
                "%(supported)s."
            )
            % {"extension": extension, "codec": codec, "supported": supported}
        )


class InvalidContainerTypeError(PyMediaError):
    """Error cuando la extensión no corresponde al tipo de medio esperado."""

    def __init__(self, extension: str, media_type: str, supported: str) -> None:
        """Inicializa el error con la extensión, el tipo de medio y los válidos.

        Args:
            extension: Extensión del fichero de salida.
            media_type: Tipo de medio de salida esperado.
            supported: Extensiones de contenedor soportadas para ese tipo.
        """
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
    """Error por un parámetro procesado con un valor no válido."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)


class InvalidTimeFormatError(PyMediaError):
    """Error por una marca de tiempo con un formato no soportado."""

    def __init__(self) -> None:
        """Inicializa el error con el formato esperado `hh:mm:ss`."""
        super().__init__(_("Invalid timestamp format. Expected: hh:mm:ss."))


class MissingArgumentError(PyMediaError):
    """Error cuando no se pudo obtener un argumento requerido."""

    def __init__(self, name: str) -> None:
        """Inicializa el error con el nombre del argumento ausente.

        Args:
            name: Nombre del argumento que falta.
        """
        super().__init__(_("Missing argument: %(name)s") % {"name": name})


class MissingMediaError(PyMediaError):
    """Error cuando no se pudieron obtener los metadatos de un vídeo."""

    def __init__(self, path: str) -> None:
        """Inicializa el error con la ruta del medio fallido.

        Args:
            path: Ruta del fichero cuyos metadatos no se obtuvieron.
        """
        super().__init__(_("Missing media information: %(path)s") % {"path": path})


class MissingMediaPropertyError(PyMediaError):
    """Error cuando falta una propiedad técnica de los metadatos del medio."""

    def __init__(self, name: str) -> None:
        """Inicializa el error con el nombre de la propiedad ausente.

        Args:
            name: Nombre de la propiedad del medio que falta.
        """
        super().__init__(_("Missing media property: %(name)s") % {"name": name})


class MissingParameterError(PyMediaError):
    """Error cuando no se pudo obtener un parámetro requerido."""

    def __init__(self, name: str) -> None:
        """Inicializa el error con el nombre del parámetro ausente.

        Args:
            name: Nombre del parámetro que falta.
        """
        super().__init__(_("Missing parameter: %(name)s") % {"name": name})


class MissingRequiredOptionError(PyMediaError):
    """Error cuando no se aporta ninguna de las opciones requeridas."""

    def __init__(self, options: list[str]) -> None:
        """Inicializa el error con las opciones que son necesarias.

        Args:
            options: Opciones de CLI de las que al menos una es obligatoria.
        """
        super().__init__(
            _("One of the following options is required: %(options)s")
            % {"options": ", ".join(options)}
        )


class OptionError(PyMediaError):
    """Error de uso de una opción de CLI."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)


class PermissionDeniedError(PyMediaError):
    """Error cuando no se tienen permisos para crear un fichero o directorio."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)


class SubtitlesError(PyMediaError):
    """Errores relacionados con subtítulos."""

    def __init__(self, msg: str) -> None:
        """Inicializa el error con el mensaje indicado.

        Args:
            msg: Mensaje de error ya formateado.
        """
        super().__init__(msg)
