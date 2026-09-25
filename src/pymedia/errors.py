"""Jerarquía de excepciones de pyMedia.

Cada subclase construye su mensaje con `_("msgid") % kwargs` en el momento de
lanzarse, de modo que usa el idioma activo del catálogo. `PyMediaError` registra
automáticamente el mensaje en el log.
"""

import logging

from typer import BadParameter, TyperException

from pymedia.locales import translate as _
from pymedia.logger import Logger
from pymedia.types import MediaType

logger = Logger(logging.getLogger("pymedia.logger"))

# =============================================================================
#  Errores de aplicación
# =============================================================================


class PyMediaError(TyperException):
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
        self.msg = f"{msg}"
        super().__init__(self.msg)
        logger.error(msg=self.msg)


class CommandError(PyMediaError):
    """Error durante la ejecución de un comando ffmpeg."""


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


class InvalidParameterError(PyMediaError):
    """Error por un parámetro procesado con un valor no válido."""


class MissingArgumentError(PyMediaError):
    """Error cuando no se pudo obtener un argumento requerido."""

    def __init__(self, name: str) -> None:
        """Inicializa el error con el nombre del argumento ausente.

        Args:
            name: Nombre del argumento que falta.
        """
        super().__init__(_("Missing argument: %(name)s") % {"name": name})


class MissingParameterError(PyMediaError):
    """Error cuando no se pudo obtener un parámetro requerido."""

    def __init__(self, name: str) -> None:
        """Inicializa el error con el nombre del parámetro ausente.

        Args:
            name: Nombre del parámetro que falta.
        """
        super().__init__(_("Missing parameter: %(name)s") % {"name": name})


class MissingPropertyError(PyMediaError):
    """Error cuando falta una propiedad técnica de los metadatos del medio."""

    def __init__(self, name: str) -> None:
        """Inicializa el error con el nombre de la propiedad ausente.

        Args:
            name: Nombre de la propiedad del medio que falta.
        """
        super().__init__(_("Missing property: %(name)s") % {"name": name})


class OsError(PyMediaError):
    """Errores de instrucciones solicitadas al sistema operativo."""


# =============================================================================
#  Errores de usuario
# =============================================================================


class UserError(BadParameter):
    """Errores de los argumentos introducidos por el usuario.

    Extiende `BadParameter` para no mostrar traceback y que el usuario tenga
    un feedback claro y simple.
    """

    def __init__(self, msg: str) -> None:
        """Inicializa el error y registra el mensaje solo en el fichero de log.

        Args:
            msg: Mensaje de error ya formateado.
        """
        self.msg = f"{msg}"
        super().__init__(message=self.msg)
        logger.error(msg=self.msg, console=False)


class FfprobeError(UserError):
    """Errores de ffprobe al leer un fichero (sin traceback para el usuario)."""


class InvalidCodecContainerError(UserError):
    """Si el usuario ha indicado un contenedor de salida incompatible con sus códecs."""

    def __init__(self, extension: str, codec: str, supported: tuple[str, ...]) -> None:
        """Inicialización del error.

        Args:
            extension: Nombre del contenedor de salida.
            codec: Nombre del códec.
            supported: Lista de contenedores soportados por el códec.
        """
        super().__init__(
            _(
                "Invalid extension %(extension)s. "
                "Codec %(codec)s requires one of: %(supported)s."
            )
            % {
                "extension": extension,
                "codec": codec,
                "supported": ", ".join(supported),
            }
        )


class InvalidContainerError(UserError):
    """Si indicado contenedor de salida incompatible con el tipo de contenido."""

    def __init__(
        self, extension: str, media_type: MediaType, supported: tuple[str, ...]
    ) -> None:
        """Inicialización del error.

        Args:
            extension: Nombre del contenedor de salida.
            media_type: Tipo de contenido multimedia.
            supported: Lista de contenedores soportados por el códec.
        """
        super().__init__(
            _(
                "Invalid extension %(extension)s. %(media)s requires one of: "
                "%(supported)s."
            )
            % {
                "extension": extension,
                "media": media_type.value.capitalize(),
                "supported": ", ".join(supported),
            }
        )


class MissingRequiredOptionsError(UserError):
    """Si el usuario no ha indicado una de las opciones requeridas."""

    def __init__(self, options: list[str]) -> None:
        """Inicialización del error.

        Args:
            options: Lista de opciones requeridas.
        """
        if len(options) == 1:
            super().__init__(
                _("Missing required option: %(options)s")
                % {"options": ", ".join(options)}
            )
        else:
            super().__init__(
                _("Missing at least one of these options: %(options)s")
                % {"options": ", ".join(options)}
            )
