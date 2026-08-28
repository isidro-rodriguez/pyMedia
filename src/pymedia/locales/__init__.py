"""
Paquete de idiomas de pyMedia.

Los diccionarios del idioma activo se exponen como atributos de este paquete
(Cli, ConfigValidation, Debug, ExecutionError, Info, ParameterError,
ValidationError, Warnings) mediante `services.locale_service.set_language()`.
"""

from typing import Any

from pymedia.services.locale_service import detect_language, set_language

Cli: dict[str, Any]
ConfigValidation: dict[str, Any]
Debug: dict[str, Any]
ExecutionError: dict[str, Any]
Info: dict[str, Any]
ParameterError: dict[str, Any]
Progress: dict[str, Any]
Sheet: dict[str, Any]
ValidationError: dict[str, Any]
Warnings: dict[str, Any]

set_language(detect_language())
