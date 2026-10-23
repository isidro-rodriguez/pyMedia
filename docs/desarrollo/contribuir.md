# Contribuir

## Entorno

Requisitos: Python 3.12+, [uv](https://docs.astral.sh/uv/) y ffmpeg/ffprobe en el
`PATH` (los tests extremo a extremo los usan).

```bash
git clone https://github.com/isidro-rodriguez/pyMedia.git
cd pyMedia
uv sync                        # un único venv y uv.lock en la raíz, con el grupo dev
uv run pre-commit install      # hooks locales (opcional, recomendado)
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

Los hooks de `.pre-commit-config.yaml` ejecutan la misma secuencia (ruff, ty y pytest)
en cada commit: `uv run pre-commit run --all-files` para lanzarlos a mano.

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

`scripts/generate_fixtures.py` genera en `local/fixtures/` un juego más completo
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
| `scripts/i18n.py`              | Mantenimiento de catálogos gettext (ver arriba).                 |
| `scripts/generate_fixtures.py` | Genera medios de prueba manual en `local/fixtures/`.             |
| `scripts/backup.py`            | Comprime `src/`, `tests/`, `scripts/` y ficheros raíz en `local/`. |
| `scripts/code_count.py`        | Cuenta líneas de código y de docstrings.                         |

Todos se ejecutan con `uv run python scripts/<script>.py`.

## Versionado y CHANGELOG

- La versión vive en `src/pymedia/__init__.py` (`version = "X.Y.Z..."`); hatchling la
  lee desde ahí. No hay tags de git.
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
