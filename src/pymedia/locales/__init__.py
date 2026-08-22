"""
Paquete de idiomas de pyMedia.

Los diccionarios del idioma activo se exponen como atributos de este paquete
(Cli, ConfigValidation, Debug, ExecutionError, Info, ParameterError,
ValidationError, Warnings) mediante `services.locale_service.set_language()`.
"""

from pymedia.services.locale_service import detect_language, set_language

set_language(detect_language())
