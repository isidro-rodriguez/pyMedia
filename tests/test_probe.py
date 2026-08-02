"""Tests de probe. De momento solo saluda, pero garantiza fixtures."""

import subprocess
import sys
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
GENERATOR = Path(__file__).parent / "utils" / "generate_test_videos.py"

EXPECTED = {
    "valid_concat": 3,
    "valid_transcode": 6,
    "invalid": 6,
}


def _fixtures_ready() -> bool:
    """Comprueba que existen los 15 archivos esperados."""
    for sub, count in EXPECTED.items():
        files = list((FIXTURES / sub).glob("*"))
        if len(files) != count:
            return False
    return True


@pytest.fixture(scope="session", autouse=True)
def ensure_fixtures() -> None:
    """Genera fixtures si no existen."""
    if not _fixtures_ready():
        subprocess.run([sys.executable, str(GENERATOR)], check=True)


def test_probe_saluda() -> None:
    """Test placeholder: solo verifica que los fixtures están listos."""
    assert _fixtures_ready()
