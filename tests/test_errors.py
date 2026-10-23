"""Tests de `pymedia.errors`: mensajes de `UserError` en el idioma activo."""

import logging
from collections.abc import Iterator

import pytest

from pymedia.errors import UserError
from pymedia.locale_manager import locale_manager


@pytest.fixture
def spanish_locale() -> Iterator[None]:
    """Activa el catálogo español durante el test y restaura el inglés."""
    locale_manager.set_language("spanish")
    yield
    locale_manager.set_language("english")


def test_user_error_message_without_param() -> None:
    """Sin opción asociada, el panel muestra solo el mensaje."""
    assert UserError("Bad input.").format_message() == "Invalid value: Bad input."


@pytest.mark.parametrize(
    ("param_hint", "expected"),
    [
        ("'--at'", "Invalid value for '--at': Bad input."),
        (("--at", "-a"), "Invalid value for '--at' / '-a': Bad input."),
    ],
)
def test_user_error_message_with_param_hint(
    param_hint: str | tuple[str, ...], expected: str
) -> None:
    """La opción se nombra como en Click, también con varios alias."""
    error = UserError("Bad input.")
    error.param_hint = param_hint
    assert error.format_message() == expected


@pytest.mark.usefixtures("spanish_locale")
def test_user_error_message_translated() -> None:
    """El texto que añade Click alrededor del mensaje sale traducido."""
    error = UserError("Mensaje.")
    assert error.format_message() == "Valor no válido: Mensaje."
    error.param_hint = "'MEDIA_FILE'"
    assert error.format_message() == "Valor no válido para 'MEDIA_FILE': Mensaje."


def test_pymedia_logger_has_null_handler() -> None:
    """Sin `Logger.create`, los mensajes no se imprimen por el último recurso."""
    handlers = logging.getLogger("pymedia").handlers
    assert any(isinstance(handler, logging.NullHandler) for handler in handlers)
