"""Tests del script de empaquetado (`scripts/package.py`)."""

import importlib.util
import shutil
import subprocess
import zipfile
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _load_package_script() -> ModuleType:
    """Importa `scripts/package.py` como módulo (no es un paquete instalable)."""
    spec = importlib.util.spec_from_file_location(
        "package_script", ROOT / "scripts" / "package.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


package = _load_package_script()


@pytest.fixture
def info() -> object:
    """Metadatos de proyecto de prueba."""
    return package.ProjectInfo(
        version="1.2.0-beta.1",
        description="Descripción de prueba.",
        maintainer="Autor <autor@example.com>",
    )


@pytest.mark.parametrize(
    ("version", "expected"),
    [("1.0.0", "1.0.0"), ("1.2.0-beta.1", "1.2.0~beta.1")],
)
def test_deb_version_orders_prereleases_first(version: str, expected: str) -> None:
    """Las prerelease usan `~` para ordenar antes que la versión final."""
    assert package.deb_version(version) == expected


def test_read_project_info_uses_the_package_version() -> None:
    """La versión sale de `src/pymedia/__init__.py`, igual que en hatchling."""
    from pymedia import version

    assert package.read_project_info().version == version


def test_release_notes_extracts_the_version_section(tmp_path: Path) -> None:
    """Las notas son la sección del CHANGELOG sin su encabezado."""
    changelog = tmp_path / "CHANGELOG.md"
    changelog.write_text(
        "# Changelog\n\n## [1.1.0] - 2026-11-01\n\n- B\n\n"
        "## [1.0.0] - 2026-10-23\n\n### Añadido\n\n- A\n",
        encoding="utf-8",
    )

    assert package.release_notes("1.0.0", changelog) == "### Añadido\n\n- A\n"
    with pytest.raises(SystemExit):
        package.release_notes("9.9.9", changelog)


def test_current_changelog_has_notes_for_the_current_version() -> None:
    """Un release no puede publicarse sin su sección en el CHANGELOG."""
    version = package.read_project_info().version

    assert package.release_notes(version).strip()


def test_desktop_entry_points_to_installed_paths() -> None:
    """El lanzador usa el ejecutable y el icono instalados por el paquete."""
    entry = package._desktop_entry()

    assert "Exec=pymedia\n" in entry
    assert "Icon=pymedia\n" in entry


def test_build_zip_contains_executable_license_and_readme(
    tmp_path: Path, info: object
) -> None:
    """El zip de Windows agrupa el ejecutable y la documentación en una carpeta."""
    binary = tmp_path / "pymedia.exe"
    binary.write_bytes(b"MZ")

    zip_path = package.build_zip(binary, info, tmp_path)

    assert zip_path.name == "pymedia-1.2.0-beta.1-windows-x64.zip"
    with zipfile.ZipFile(zip_path) as archive:
        assert sorted(archive.namelist()) == [
            "pymedia-1.2.0-beta.1/LICENSE.txt",
            "pymedia-1.2.0-beta.1/README.md",
            "pymedia-1.2.0-beta.1/pymedia.exe",
        ]


def test_write_checksum_matches_sha256sum_format(tmp_path: Path) -> None:
    """El checksum sigue el formato `<hash>  <fichero>` de `sha256sum`."""
    artifact = tmp_path / "pymedia.zip"
    artifact.write_bytes(b"abc")

    checksum = package.write_checksum(artifact)

    assert checksum.read_text(encoding="utf-8") == (
        "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
        "  pymedia.zip\n"
    )


@pytest.mark.skipif(shutil.which("dpkg-deb") is None, reason="requiere dpkg-deb")
def test_build_deb_installs_binary_manpage_icon_and_launcher(
    tmp_path: Path, info: object
) -> None:
    """El .deb declara ffmpeg como dependencia e instala todos los recursos."""
    binary = tmp_path / "pymedia"
    binary.write_bytes(b"#!/bin/sh\n")

    deb = package.build_deb(binary, info, "amd64", tmp_path)

    assert deb.name == "pymedia_1.2.0~beta.1_amd64.deb"
    fields = subprocess.run(
        ["dpkg-deb", "--field", str(deb), "Package", "Version", "Depends"],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    assert "Version: 1.2.0~beta.1" in fields
    assert "Depends: ffmpeg" in fields
    contents = subprocess.run(
        ["dpkg-deb", "--contents", str(deb)],
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for path in (
        "-rwxr-xr-x root/root",
        "./usr/bin/pymedia",
        "./usr/share/man/man1/pymedia.1.gz",
        "./usr/share/applications/pymedia.desktop",
        "./usr/share/icons/hicolor/256x256/apps/pymedia.png",
        "./usr/share/doc/pymedia/copyright",
    ):
        assert path in contents
