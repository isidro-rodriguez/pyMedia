"""Empaqueta el ejecutable compilado para su distribución.

Uso:
    uv run python scripts/build.py              # compila build/pymedia(.exe)
    uv run python scripts/package.py            # paquete de la plataforma actual
    uv run python scripts/package.py notes      # notas de la versión (CHANGELOG)

Genera en `dist/`, junto a un fichero `.sha256` por paquete:
    Linux:   pymedia_<versión>_<arquitectura>.deb
    Windows: pymedia-<versión>-windows-x64.zip
"""

import argparse
import gzip
import hashlib
import re
import shutil
import subprocess
import sys
import tomllib
import zipfile
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"
RESOURCES = ROOT / "src" / "pymedia" / "resources"
HOMEPAGE = "https://github.com/isidro-rodriguez/pyMedia"


@dataclass(frozen=True, slots=True)
class ProjectInfo:
    """Metadatos del proyecto necesarios para empaquetar.

    Attributes:
        version: Versión de pyMedia (`src/pymedia/__init__.py`).
        description: Descripción corta de `pyproject.toml`.
        maintainer: Autor en formato `Nombre <email>`.
    """

    version: str
    description: str
    maintainer: str


def read_project_info(root: Path = ROOT) -> ProjectInfo:
    """Lee la versión y los metadatos del proyecto.

    Args:
        root: Raíz del repositorio.

    Returns:
        Metadatos del proyecto.

    Raises:
        SystemExit: Si no se encuentra la versión en `src/pymedia/__init__.py`.
    """
    init = (root / "src" / "pymedia" / "__init__.py").read_text(encoding="utf-8")
    match = re.search(r'^version = "([^"]+)"', init, re.MULTILINE)
    if match is None:
        raise SystemExit("No se encontró la versión en src/pymedia/__init__.py")
    with (root / "pyproject.toml").open("rb") as file:
        project = tomllib.load(file)["project"]
    author = project["authors"][0]
    return ProjectInfo(
        version=match.group(1),
        description=project["description"],
        maintainer=f"{author['name']} <{author['email']}>",
    )


def deb_version(version: str) -> str:
    """Convierte una versión de pyMedia al formato de Debian.

    El sufijo de prelanzamiento usa `~` para que ordene antes que la final.

    Args:
        version: Versión de pyMedia (p. ej. `1.0.0` o `1.1.0-beta.1`).

    Returns:
        Versión de Debian (p. ej. `1.0.0` o `1.1.0~beta.1`).

    Examples:
        >>> deb_version("1.1.0-beta.1")
        '1.1.0~beta.1'
    """
    return version.replace("-", "~", 1)


# =============================================================================
#  Linux: paquete .deb
# =============================================================================


def build_deb(binary: Path, info: ProjectInfo, arch: str, out_dir: Path) -> Path:
    """Construye el paquete `.deb` con el ejecutable, man page, icono y lanzador.

    Args:
        binary: Ejecutable compilado con PyInstaller.
        info: Metadatos del proyecto.
        arch: Arquitectura de Debian (`amd64`, `arm64`…).
        out_dir: Directorio de salida.

    Returns:
        Ruta del `.deb` generado.

    Raises:
        subprocess.CalledProcessError: Si `dpkg-deb` falla.
    """
    version = deb_version(info.version)
    staging = out_dir / f"pymedia_{version}_{arch}"
    shutil.rmtree(staging, ignore_errors=True)

    _install(binary, staging / "usr" / "bin" / "pymedia", mode=0o755)
    _install_gzip(RESOURCES / "pymedia.1", staging / "usr/share/man/man1/pymedia.1.gz")
    _install(
        RESOURCES / "icon.png",
        staging / "usr/share/icons/hicolor/256x256/apps/pymedia.png",
    )
    _write(staging / "usr/share/applications/pymedia.desktop", _desktop_entry())
    _write(staging / "usr/share/doc/pymedia/copyright", _copyright(info))
    _write(staging / "DEBIAN" / "control", _control(info, version, arch, staging))

    package = out_dir / f"{staging.name}.deb"
    subprocess.run(
        ["dpkg-deb", "--build", "--root-owner-group", str(staging), str(package)],
        check=True,
    )
    shutil.rmtree(staging)
    return package


def _install(source: Path, target: Path, mode: int = 0o644) -> None:
    """Copia un fichero al árbol del paquete con los permisos indicados."""
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, target)
    target.chmod(mode)


def _install_gzip(source: Path, target: Path) -> None:
    """Copia un fichero comprimido con gzip (mtime 0, reproducible)."""
    target.parent.mkdir(parents=True, exist_ok=True)
    with (
        target.open("wb") as raw,
        gzip.GzipFile(
            filename="", mode="wb", compresslevel=9, fileobj=raw, mtime=0
        ) as gz,
    ):
        gz.write(source.read_bytes())
    target.chmod(0o644)


def _write(target: Path, content: str) -> None:
    """Escribe un fichero de texto del paquete."""
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    target.chmod(0o644)


def _desktop_entry() -> str:
    """Adapta el lanzador de `resources` a las rutas instaladas por el paquete."""
    lines = (RESOURCES / "pymedia.desktop").read_text(encoding="utf-8").splitlines()
    fixed = {"Exec": "pymedia", "Icon": "pymedia"}
    return (
        "\n".join(
            f"{key}={fixed[key]}" if (key := line.partition("=")[0]) in fixed else line
            for line in lines
        )
        + "\n"
    )


def _copyright(info: ProjectInfo) -> str:
    """Fichero de copyright en formato DEP-5."""
    license_text = (ROOT / "LICENSE").read_text(encoding="utf-8").strip()
    body = "\n".join(f" {line}" if line else " ." for line in license_text.splitlines())
    return (
        "Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/\n"
        "Upstream-Name: pymedia\n"
        f"Source: {HOMEPAGE}\n\n"
        "Files: *\n"
        f"Copyright: 2026 {info.maintainer}\n"
        f"License: MIT\n{body}\n"
    )


def _control(info: ProjectInfo, version: str, arch: str, staging: Path) -> str:
    """Fichero `DEBIAN/control` con el tamaño instalado calculado."""
    size_kib = sum(f.stat().st_size for f in staging.rglob("*") if f.is_file()) // 1024
    return (
        "Package: pymedia\n"
        f"Version: {version}\n"
        f"Architecture: {arch}\n"
        f"Maintainer: {info.maintainer}\n"
        f"Installed-Size: {max(size_kib, 1)}\n"
        "Depends: ffmpeg\n"
        "Section: video\n"
        "Priority: optional\n"
        f"Homepage: {HOMEPAGE}\n"
        f"Description: {info.description.rstrip('.')}\n"
        " CLI sencilla para ffmpeg: analiza, corta, une, convierte y edita\n"
        " vídeos, pistas de audio y subtítulos con comandos cortos.\n"
    )


def debian_arch() -> str:
    """Arquitectura de Debian del sistema actual (`amd64` si no hay dpkg)."""
    try:
        result = subprocess.run(
            ["dpkg", "--print-architecture"], capture_output=True, text=True, check=True
        )
    except (OSError, subprocess.CalledProcessError):
        return "amd64"
    return result.stdout.strip()


# =============================================================================
#  Windows: paquete .zip
# =============================================================================


def build_zip(binary: Path, info: ProjectInfo, out_dir: Path) -> Path:
    """Construye el `.zip` con el ejecutable, la licencia y el README.

    Args:
        binary: Ejecutable compilado con PyInstaller.
        info: Metadatos del proyecto.
        out_dir: Directorio de salida.

    Returns:
        Ruta del `.zip` generado.
    """
    package = out_dir / f"pymedia-{info.version}-windows-x64.zip"
    folder = f"pymedia-{info.version}"
    with zipfile.ZipFile(package, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(binary, f"{folder}/pymedia.exe")
        archive.write(ROOT / "LICENSE", f"{folder}/LICENSE.txt")
        archive.write(ROOT / "README.md", f"{folder}/README.md")
    return package


# =============================================================================
#  Utilidades comunes
# =============================================================================


def write_checksum(package: Path) -> Path:
    """Escribe `<paquete>.sha256` en el formato de `sha256sum`.

    Args:
        package: Paquete del que calcular el hash.

    Returns:
        Ruta del fichero de checksum.
    """
    digest = hashlib.sha256(package.read_bytes()).hexdigest()
    checksum = package.with_name(f"{package.name}.sha256")
    checksum.write_text(f"{digest}  {package.name}\n", encoding="utf-8")
    return checksum


def release_notes(version: str, changelog: Path = ROOT / "CHANGELOG.md") -> str:
    """Extrae del CHANGELOG la sección de una versión.

    Args:
        version: Versión cuya sección se busca (sin `v`).
        changelog: Ruta del CHANGELOG.

    Returns:
        Contenido de la sección, sin su encabezado.

    Raises:
        SystemExit: Si el CHANGELOG no tiene sección para la versión.
    """
    text = changelog.read_text(encoding="utf-8")
    pattern = rf"^## \[{re.escape(version)}\][^\n]*\n(.*?)(?=^## \[|\Z)"
    match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
    if match is None:
        raise SystemExit(f"CHANGELOG.md no tiene sección para la versión {version}")
    return match.group(1).strip() + "\n"


def package_current_platform() -> Path:
    """Empaqueta el ejecutable de `build/` para la plataforma actual.

    Returns:
        Ruta del paquete generado.

    Raises:
        SystemExit: Si falta el ejecutable o la plataforma no está soportada.
    """
    info = read_project_info()
    DIST_DIR.mkdir(exist_ok=True)
    if sys.platform == "win32":
        binary = BUILD_DIR / "pymedia.exe"
        _require(binary)
        return build_zip(binary, info, DIST_DIR)
    if sys.platform.startswith("linux"):
        binary = BUILD_DIR / "pymedia"
        _require(binary)
        return build_deb(binary, info, debian_arch(), DIST_DIR)
    raise SystemExit(f"Plataforma no soportada para empaquetar: {sys.platform}")


def _require(binary: Path) -> None:
    """Comprueba que el ejecutable exista antes de empaquetar."""
    if not binary.is_file():
        raise SystemExit(f"No existe {binary}. Ejecuta antes scripts/build.py.")


def main() -> None:
    """Punto de entrada del script."""
    parser = argparse.ArgumentParser(description="Empaquetado de pyMedia.")
    parser.add_argument(
        "action",
        nargs="?",
        choices=["package", "notes"],
        default="package",
        help="package: crea el paquete; notes: imprime las notas de la versión.",
    )
    args = parser.parse_args()

    if args.action == "notes":
        sys.stdout.write(release_notes(read_project_info().version))
        return

    package = package_current_platform()
    checksum = write_checksum(package)
    print(f"Paquete: {package}\nChecksum: {checksum}")


if __name__ == "__main__":
    main()
