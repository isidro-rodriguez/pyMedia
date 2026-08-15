"""Tests para pymedia.logger."""

import logging
import sys
from pathlib import Path

import pytest

from pymedia import locales
from pymedia.logger import (
    AbbrevFormatter,
    AnsiColorFormatter,
    PymediaFilter,
    get_logger,
    log_debug,
    log_info,
    log_warning,
    setup_logging,
)


# -----------------------------------------------------------------------------
#  setup_logging()
# -----------------------------------------------------------------------------


def test_setup_logging_idempotent():
    """setup_logging() se puede llamar varias veces sin efectos secundarios."""
    setup_logging()
    setup_logging()
    setup_logging()


def test_setup_logging_requires_first_call():
    """setup_logging() debe llamarse una vez antes de configurar debug."""
    # Reset the module state for testing
    import pymedia.logger as logger_mod
    logger_mod._configured = False
    setup_logging(debug=True)
    root = logging.getLogger()
    assert root.level == logging.DEBUG


def test_setup_logging_sets_root_level():
    """setup_logging() configura el nivel del logger raíz."""
    # Reset the module state for testing
    import pymedia.logger as logger_mod
    logger_mod._configured = False
    setup_logging()
    root = logging.getLogger()
    assert root.level == logging.INFO


def test_setup_logging_debug_level():
    """setup_logging(debug=True) configura el nivel en DEBUG."""
    # Reset the module state for testing
    import pymedia.logger as logger_mod
    logger_mod._configured = False
    setup_logging(debug=True)
    root = logging.getLogger()
    assert root.level == logging.DEBUG


# -----------------------------------------------------------------------------
#  get_logger()
# -----------------------------------------------------------------------------


def test_get_logger_returns_pymedia_logger():
    """get_logger() devuelve un logger con prefijo 'pymedia'."""
    logger = get_logger()
    assert logger.name == "pymedia"


def test_get_logger_with_name():
    """get_logger('custom') devuelve un logger con nombre personalizado."""
    logger = get_logger("custom")
    assert logger.name == "pymedia.custom"


# -----------------------------------------------------------------------------
#  AbbrevFormatter
# -----------------------------------------------------------------------------


def test_abbrev_formatter_debug():
    """AbbrevFormatter.abbrevia DEBUG tal cual."""
    formatter = AbbrevFormatter("%(levelname)s %(message)s")
    record = logging.LogRecord("pymedia.test", logging.DEBUG, "", 0, "test message", (), None)
    result = formatter.format(record)
    assert "[DEBUG]" in result


def test_abbrev_formatter_info():
    """AbbrevFormatter.abbrevia INFO tal cual."""
    formatter = AbbrevFormatter("%(levelname)s %(message)s")
    record = logging.LogRecord("pymedia.test", logging.INFO, "", 0, "test message", (), None)
    result = formatter.format(record)
    assert "[INFO]" in result


def test_abbrev_formatter_warning():
    """AbbrevFormatter.abbrevia WARNING a [WARN]."""
    formatter = AbbrevFormatter("%(levelname)s %(message)s")
    record = logging.LogRecord("pymedia.test", logging.WARNING, "", 0, "test message", (), None)
    result = formatter.format(record)
    assert "[WARN]" in result


def test_abbrev_formatter_error():
    """AbbrevFormatter.abbrevia ERROR a [ERROR]."""
    formatter = AbbrevFormatter("%(levelname)s %(message)s")
    record = logging.LogRecord("pymedia.test", logging.ERROR, "", 0, "test message", (), None)
    result = formatter.format(record)
    assert "[ERROR]" in result


def test_abbrev_formatter_critical():
    """AbbrevFormatter.abbrevia CRITICAL a [CRIT]."""
    formatter = AbbrevFormatter("%(levelname)s %(message)s")
    record = logging.LogRecord("pymedia.test", logging.CRITICAL, "", 0, "test message", (), None)
    result = formatter.format(record)
    assert "[CRIT]" in result


# -----------------------------------------------------------------------------
#  AnsiColorFormatter
# -----------------------------------------------------------------------------


def test_ansi_color_formatter_has_color_codes():
    """AnsiColorFormatter agrega códigos de color ANSI."""
    formatter = AnsiColorFormatter("%(levelname)s %(message)s")
    record = logging.LogRecord("pymedia.test", logging.INFO, "", 0, "test message", (), None)
    result = formatter.format(record)
    # Debe contener códigos ANSI (colores azul para INFO)
    assert "\033[34m" in result  # blue


def test_ansi_color_formatter_resets_style():
    """AnsiColorFormatter reinicia el estilo al final."""
    formatter = AnsiColorFormatter("%(levelname)s %(message)s")
    record = logging.LogRecord("pymedia.test", logging.INFO, "", 0, "test message", (), None)
    result = formatter.format(record)
    assert "\033[0m" in result  # no_style (reset)


# -----------------------------------------------------------------------------
#  PymediaFilter
# -----------------------------------------------------------------------------


def test_pymedia_filter_pymedia_logger():
    """PymediaFilter deja pasar loggers que empiezan con 'pymedia'."""
    filt = PymediaFilter()
    record = logging.LogRecord("pymedia.test", logging.INFO, "", 0, "test message", (), None)
    assert filt.filter(record) is True


def test_pymedia_filter_other_logger():
    """PymediaFilter bloquea loggers que no empiezan con 'pymedia'."""
    filt = PymediaFilter()
    record = logging.LogRecord("other.test", logging.INFO, "", 0, "test message", (), None)
    assert filt.filter(record) is False


# -----------------------------------------------------------------------------
#  log_info / log_warning / log_debug
# -----------------------------------------------------------------------------


def test_log_info_uses_locale_template(monkeypatch):
    """log_info usa la plantilla locales.Info."""
    # Monkeypatchear el diccionario para evitar dependencia de configuración activa
    original = locales.Info.copy()
    try:
        locales.Info["test_key"] = "Mensaje de prueba: {param}"
        logger = get_logger()
        log_info(logger, "test_key", param="valor")
        # Capturar el output
        from io import StringIO
        import logging as logmod
        handler = logmod.StreamHandler(StringIO())
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        log_info(logger, "test_key", param="valor")
        record = handler.stream.getvalue()
        assert "Mensaje de prueba: valor" in record
    finally:
        locales.Info.clear()
        locales.Info.update(original)


def test_log_warning_uses_locale_template(monkeypatch):
    """log_warning usa la plantilla locales.Warnings."""
    original = locales.Warnings.copy()
    try:
        locales.Warnings["test_key"] = "Advertencia: {param}"
        logger = get_logger()
        log_warning(logger, "test_key", param="algo")
        from io import StringIO
        import logging as logmod
        handler = logmod.StreamHandler(StringIO())
        logger.addHandler(handler)
        logger.setLevel(logging.WARNING)
        log_warning(logger, "test_key", param="algo")
        record = handler.stream.getvalue()
        assert "Advertencia: algo" in record
    finally:
        locales.Warnings.clear()
        locales.Warnings.update(original)


def test_log_debug_uses_locale_template(monkeypatch):
    """log_debug usa la plantilla locales.Debug."""
    original = locales.Debug.copy()
    try:
        locales.Debug["test_key"] = "Depuración: {param}"
        logger = get_logger()
        log_debug(logger, "test_key", param="datos")
        from io import StringIO
        import logging as logmod
        handler = logmod.StreamHandler(StringIO())
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
        log_debug(logger, "test_key", param="datos")
        record = handler.stream.getvalue()
        assert "Depuración: datos" in record
    finally:
        locales.Debug.clear()
        locales.Debug.update(original)