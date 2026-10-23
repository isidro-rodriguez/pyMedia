# Contribuir

## Entorno

Requisitos: Python 3.12+, [uv](https://docs.astral.sh/uv/) y ffmpeg/ffprobe en el
`PATH` (los tests extremo a extremo los usan).

```bash
git clone https://github.com/isidro-rodriguez/pyMedia.git
cd pyMedia
uv sync                        # un único venv y uv.lock en la raíz, con el grupo dev
uv run pre-commit install      # hooks de pre-commit y pre-push (recomendado)
```

- Dependencias de ejecución: `uv add <paquete>`. De desarrollo: `uv add --dev <paquete>`.
- Nunca uses `pip install`.
- Antes de añadir una dependencia, comprueba si la biblioteca estándar lo resuelve.

| Grupo      | Paquetes                                                                 |
|------------|--------------------------------------------------------------------------|
| Ejecución  | `typer`, `rich`, `platformdirs`                                          |
| Desarrollo | `ruff`, `ty`, `pytest`, `pytest-cov`, `pre-commit`, `babel`, `pyinstaller`, `pdoc`, `zstandard` |

## Calidad

Ejecuta siempre desde la raíz y en este orden, deteniéndote en el primer fallo:

```bash
uv run ruff format .
uv run ruff check --fix .
uv run ruff check .
uv run ty check
uv run pytest
```

| Herramienta | Configuración (`pyproject.toml`)                                            |
|-------------|------------------------------------------------------------------------------|
| Ruff        | Línea de 88; reglas `E`, `F`, `I`, `UP`, `B`, `D`; docstrings estilo Google. |
| ty          | Python 3.12, igualdad y genéricos estrictos.                                 |
| pytest      | `tests/`, `pythonpath = src`, excluye por defecto las marcas `binary` y `locales`. |

### Hooks de git

`.pre-commit-config.yaml` instala dos etapas:

| Etapa        | Hooks                                                                     |
|--------------|---------------------------------------------------------------------------|
| `pre-commit` | `ruff check --fix`, `ruff format`, `ruff check`, `ty check`, `pytest`.    |
| `pre-push`   | `pytest --cov` (mínimo 95 %), `pytest -m locales`, `pytest -m binary`.    |

```bash
uv run pre-commit run --all-files                         # etapa pre-commit
uv run pre-commit run --all-files --hook-stage pre-push   # etapa pre-push
```

### Integración continua

`.github/workflows/ci.yml` se ejecuta en cada push a `main` y en cada pull request:

| Job       | Plataformas                         | Pasos                                                         |
|-----------|-------------------------------------|---------------------------------------------------------------|
| `quality` | Ubuntu y Windows × Python 3.12/3.13 | `ruff format --check`, `ruff check`, `ty`, `pytest --cov` (≥ 95 %), `pytest -m locales`. |
| `binary`  | Ubuntu y Windows                    | `pytest -m binary` y publica el ejecutable como artefacto (7 días). |

`.github/dependabot.yml` revisa cada lunes las dependencias de `uv` (agrupando
actualizaciones menores) y las versiones de las GitHub Actions.

## Estilo de código

- Identificadores en inglés; docstrings, comentarios y mensajes de usuario en español
  (los `msgid` de gettext, en inglés).
- Docstrings Google completos en lo público; una línea en lo privado. Las funciones
  públicas heredan en `Raises` las excepciones de las privadas que llaman.
- Funciones pequeñas (~20 líneas) con una sola responsabilidad.
- Tipado estricto; sin argumentos por defecto mutables.
- Los comentarios explican el *porqué*, no el *qué*.
- Nunca silencies errores: traduce a una excepción de `errors.py` con `from err`.

## Tests

```bash
uv run pytest                     # suite rápida (~1 100 tests)
uv run pytest -m locales          # integridad de catálogos gettext
uv run pytest -m binary           # contra el ejecutable compilado (lento: compila con PyInstaller)
uv run pytest --cov=pymedia       # cobertura
```

| Fichero                         | Ámbito                                                           |
|---------------------------------|------------------------------------------------------------------|
| `test_cli.py`                   | Escenarios extremo a extremo de cada comando.                    |
| `test_cli_options.py`           | Opciones compartidas, parametrizadas por comando.                |
| `test_regressions.py`           | Errores corregidos que no deben reaparecer.                      |
| `test_*_cmd.py`                 | Composición de comandos ffmpeg.                                  |
| `test_mixins_*.py`, `test_filters_mixin.py` | Validaciones y fragmentos de los mixins.             |
| `test_ffmpeg_runner.py`, `test_base_service.py` | Ejecución, staging, progreso, bloqueos, sobrescritura. |
| `test_ffprobe.py`, `test_utils.py` | Lectura y conversión de metadatos.                            |
| `test_config.py`                | Carga y validación de `config.toml`.                             |
| `test_data_consistency.py`      | Coherencia entre catálogos de códecs y contenedores.             |
| `test_locales.py`, `test_locale_manager.py` | Catálogos y detección de idioma.                     |

### Fixtures

- `tests/conftest.py` genera con ffmpeg medios sintéticos diminutos (2 s, 160×90)
  una vez por sesión, y fuerza el idioma inglés para que las aserciones no dependan
  del sistema.
- La fixture `pymedia` ejecuta cada escenario de dos formas: `[cli]` (en proceso, con
  `CliRunner`) y `[binary]` (el ejecutable compilado, marca `binary`). Escribe los tests
  extremo a extremo contra ella y ambos caminos quedan cubiertos.
- `helpers.py` ofrece utilidades sobre ffprobe (`stream_types`, `ffprobe_streams`…).

### Fixtures manuales

`scripts/generate_fixtures.py` genera en `tests/fixtures/` (ignorado por git) un juego más completo
(varias pistas de audio y subtítulos, vídeos verticales, sin metadatos…) para pruebas
manuales. No lo usa la suite automática.

```bash
uv run python scripts/generate_fixtures.py
```

### Reglas

- Cubre la lógica relevante y cada error corregido (en `test_regressions.py` si es
  de comportamiento visible).
- Prioriza tests útiles y legibles sobre la cobertura del 100 %.
- Los tests deben pasar en Linux y Windows: no dependas de `os.name`, separadores de
  ruta ni del idioma del sistema (usa `monkeypatch`).

## Traducciones

Los textos del código son `msgid` en inglés. Si añades o cambias mensajes:

```bash
uv run python scripts/i18n.py extract              # regenera locales/pymedia.pot
uv run python scripts/i18n.py update -l spanish    # sincroniza el .po con el POT
# traduce las entradas vacías o fuzzy de locales/spanish/LC_MESSAGES/pymedia.po
uv run python scripts/i18n.py compile -l spanish   # genera pymedia.mo
uv run python scripts/i18n.py check                # valida POT y catálogos
uv run pytest -m locales
```

- Mantén los mismos marcadores `%(nombre)s` en `msgid` y `msgstr`.
- Usa nombres de marcador simples (`%(path)s`, `%(reason)s`).
- Reutiliza `msgid` existentes antes de crear variantes casi idénticas.
- Para un idioma nuevo: añádelo a `LANGUAGES` en `scripts/i18n.py`, a
  `SUPPORTED_LANGUAGES` en `locale_manager.py` y a `SUPPORTED.LANGUAGES`.

## Scripts

| Script                         | Uso                                                              |
|--------------------------------|------------------------------------------------------------------|
| `scripts/build.py`             | Compila el ejecutable único con PyInstaller en `build/`.         |
| `scripts/package.py`           | Empaqueta el ejecutable en `dist/`: `.deb` en Linux, `.zip` en Windows, con `.sha256`. `notes` imprime las notas de la versión desde el CHANGELOG. |
| `scripts/i18n.py`              | Mantenimiento de catálogos gettext (ver arriba).                 |
| `scripts/generate_fixtures.py` | Genera medios de prueba manual en `tests/fixtures/`.             |

Todos se ejecutan con `uv run python scripts/<script>.py`.

## Documentación

La documentación es un sitio estático generado con [Zensical](https://zensical.org/)
a partir de `docs/` y publicado en GitHub Pages por el workflow `docs.yml` en cada
push a `main`.

| Ruta                                 | Contenido                                               |
|--------------------------------------|---------------------------------------------------------|
| `zensical.toml`                      | Navegación, tema, extensiones de Markdown.              |
| `docs/assets/stylesheets/pymedia.css`| Colores de la paleta de la CLI (`theme.py`) y estilos.  |
| `docs_templates/`                    | Plantillas propias: favicons y manifiesto web.          |

```bash
uv run zensical serve        # vista previa con recarga en http://localhost:8000
uv run zensical build        # genera site/ (ignorado por git)
```

- Una página nueva se añade también a `nav` en `zensical.toml`.
- Los enlaces entre páginas son relativos al fichero `.md`; no enlaces fuera de
  `docs/` (usa la URL de GitHub).
- Usa admoniciones (`!!! note`, `!!! tip`, `!!! warning`) para avisos y pestañas
  (`=== "Linux"`) para instrucciones por plataforma.
- El build debe terminar con «No issues found».

## Versionado y CHANGELOG

- La versión vive en `src/pymedia/__init__.py` (`version = "X.Y.Z"`); hatchling y
  `scripts/package.py` la leen desde ahí. Cada versión publicada tiene su tag `vX.Y.Z`.
- Se sigue [SemVer](https://semver.org/lang/es/): MAJOR para cambios incompatibles de
  la CLI, MINOR para funcionalidad nueva compatible, PATCH para correcciones y
  refactors internos.
- `CHANGELOG.md` sigue [Keep a Changelog](https://keepachangelog.com/es-ES/) en
  español: entradas bajo `## [Sin publicar]` mientras se trabaja, agrupadas en
  `### Añadido`, `### Cambiado`, `### Corregido`, `### Eliminado`, `### Obsoleto` y
  `### Seguridad`. Al publicar, la sección pasa a `## [X.Y.Z] - AAAA-MM-DD`.
- Antes de cada `git push` con cambios de código: sube la versión y actualiza el
  CHANGELOG. Si cambian restricciones de dependencias, ejecuta `uv sync` y commitea
  `uv.lock`.
- Las prerelease usan sufijo (`1.1.0-beta.1`); en el `.deb` se convierte en
  `1.1.0~beta.1` para que ordene antes de la versión final.

## Publicar una versión

1. Sube la versión en `src/pymedia/__init__.py` y renombra `## [Sin publicar]` a
   `## [X.Y.Z] - AAAA-MM-DD` en el CHANGELOG.
2. Pasa la [definición de terminado](#definición-de-terminado), incluidos los hooks
   de `pre-push`.
3. Opcional: lanza a mano el workflow **Release** (*Actions → Release → Run workflow*)
   para descargar y probar los paquetes antes de etiquetar.
4. Etiqueta y publica:

   ```bash
   git tag -a vX.Y.Z -m "pyMedia X.Y.Z"
   git push origin main vX.Y.Z
   ```

`.github/workflows/release.yml` entonces:

| Paso                | Linux (`ubuntu-22.04`)                     | Windows                          |
|---------------------|--------------------------------------------|----------------------------------|
| Comprueba el tag    | `vX.Y.Z` debe coincidir con la versión del paquete | Igual                    |
| Compila             | `scripts/build.py`                         | `scripts/build.py`               |
| Prueba              | `pymedia --version`, instala el `.deb` con `apt` | `pymedia.exe --version`    |
| Empaqueta           | `pymedia_X.Y.Z_amd64.deb` + `.sha256`      | `pymedia-X.Y.Z-windows-x64.zip` + `.sha256` |

Por último crea el GitHub Release con los cuatro ficheros y la sección del CHANGELOG
como notas (marcado como *prerelease* si el tag tiene sufijo). El ejecutable de Linux
se compila en Ubuntu 22.04 para que funcione también en distribuciones con una glibc
más antigua que la actual.

Para generar los paquetes en local:

```bash
uv run python scripts/build.py
uv run python scripts/package.py
```

## Commits

[Conventional Commits](https://www.conventionalcommits.org/es/) en español, atómicos y
explicando el porqué:

```text
feat: añade comando clean para eliminar metadatos
fix: corrige falso bloqueo en comandos sin -progress
docs: documenta los filtros de imagen
test: cubre marcas de tiempo duplicadas
chore: bump versión a 0.22.0
```

No mezcles cambios no relacionados en un mismo commit.

## Definición de terminado

Una tarea está terminada cuando:

- [ ] `ruff format --check`, `ruff check`, `ty check` y `pytest` pasan sin errores.
- [ ] Si se tocaron mensajes: catálogos actualizados y `pytest -m locales` en verde.
- [ ] Si se tocó el comportamiento de la CLI: `pytest -m binary` en verde.
- [ ] `README.md` y `docs/` actualizados si cambia el uso o las opciones.
- [ ] Entrada en `CHANGELOG.md`; versión subida antes de publicar.
