# Changelog

Formato esquemático basado en [Keep a Changelog](https://keepachangelog.com/).
Las versiones se han reconstruido a partir del histórico de
`src/pymedia/__init__.py` (el repositorio no usa tags de git).
Las versiones intermedias no registradas (0.2–0.4, 0.6–0.8) se agrupan
con la sección anterior.

## [0.16.1-beta.6] - 2026-09-18

### Cambiado

- Arquitectura de comandos: `audio`, `subtitles` y `thumb` pasan de ser un
  pipeline fragmentado con subcomandos anidados a **comandos independientes**
  (uno por paquete `commands/<cmd>`), siguiendo el mismo patrón que
  `cut`/`join`/`remux`/`transcode`/`animated`/`sheet`
- Eliminados los directorios legacy `pipeline/`, `typer/commands/` y
  `ffmpeg/` de comandos que ya no se usan (`audio_pipeline.py`,
  `subtitles_pipeline.py`, `thumb_pipeline.py`, `audio_commands.py`,
  `subtitles_commands.py`, `thumb_commands.py`, `audio_cmd.py`,
  `subtitles_cmd.py`, `thumb_cmd.py`, `AudioParameters`/`SubtitlesParameters`)
- Estructura del proyecto actualizada en README: `pipeline/` y
  `typer/commands/` ya no son módulos del proyecto

### Interno

- `types.py`: eliminados los enums `AudioMode` y `SubtitlesMode` (sin uso)
- `base_parameters.py`: eliminadas `AudioParameters` y `SubtitlesParameters`
  (solo `BaseParameters` y `ThumbParameters`)
- Los pipelines migraron a un servicio por comando con `Parameters.load()`,
  `Cmd.create()` y `Service.start()` siguiendo la misma convención

## [0.16.0-beta.0] - 2026-09-17 → presente

### Añadido
- Opción global `--version`: panel Rich con versión, Python y plataforma
- Comando `cut`: corte por rango de tiempo (`--start`/`--end`) y división por
  marcas (`--at`), con validación de opciones excluyentes
- Error `MissingRequiredOptionsError` para `cut` y `transcode`

### Cambiado
- Comando `split` renombrado a `cut` (CLI, pipeline, ayuda, man page y tests)
- Locales `es` regenerados y compilados (`pymedia.pot`/`.po`/`.mo`)
- README actualizado al comando `cut`
- Los pipelines pasan a `run_ffmpeg` los ficheros de salida esperados para
  eliminarlos si el comando se interrumpe, agota el tiempo o falla
- `run_ffmpeg` acepta un iterable perezoso de salidas (uso en `thumb --scene`,
  cuyo número de ficheros solo se conoce al terminar ffmpeg)
- `audio`/`subtitles --extract`: la limpieza de abort usa las rutas reales de
  los ficheros extraídos (antes pasaba la salida de medios, inexistente en
  dicho modo)

## [0.15.0-beta.0] - 2026-09-17

### Añadido
- Opción `--burn-subtitles` en `transcode`: quema un fichero de subtítulos en
  la pista de vídeo (filtro `subtitles` integrado en el grafo `filter_complex`)
- Validación del fichero de subtítulos (`validate_subtitles_file_codec`)
- Tests de `to_burn_subtitles_cmd` y del flujo `transcode --burn-subtitles`

## [0.14.0-beta.0] - 2026-09-11 → 2026-09-17

### Añadido
- Tests E2E del binario PyInstaller (`tests/test_binary_e2e.py`)
- Hook de pre-commit para el binario compilado
- Campos de duración de pistas de vídeo/audio

### Cambiado
- Portado del empaquetado del ejecutable a PyInstaller
- README y página man actualizados
- Docstrings completados en toda la base de código

### Interno
- Pre-commit configurado (ruff, mypy, pytest)
- Correcciones de tipado con mypy estricto

## [0.13.0] - 2026-09-11

### Añadido
- Comando `join`: unión de vídeos compatibles sin recodificar

## [0.12.0] - 2026-09-10

### Añadido
- Comando `split`: división de ficheros por marcas de tiempo

## [0.11.0] - 2026-09-10

### Añadido
- Pipeline completo del comando `transcode`
- Sistema de presets de transcode en `config.toml`

### Cambiado
- Filtros refactorizados a `FiltersMixin`
- Refactorización de la gestión de sobrescritura de salidas

## [0.10.0] - 2026-09-09

### Añadido
- Familia de comandos de audio (extracción y conversión)

## [0.9.0] - 2026-09-06

### Añadido
- Comando `subtitles add`: incrustado de pistas de subtítulos
- Catálogo completo de contenedores soportados

### Cambiado
- Refactorización del módulo de containers

## [0.5.0] - 2026-08-16 → 2026-09-05

### Añadido
- Sistema de locales con gettext (es/en)
- Comando `info`: metadatos vía ffprobe (incluye perfil de códec)
- Comando `sheet`: contact sheet con cabecera localizada y metadatos
- Comando `thumbnail`
- Mixins de transformación: rotate, flip
- Opción `crop` en `gif`; fps reducido a 12
- Códigos de idioma según ISO 639-2
- Tests de utils y de locales

### Cambiado
- CLI refactorizada: comandos migrados a clases (`GifCmd`, `SheetCmd`, ...)
- Refactorización de scale, errores y pipeline de capturas
- Opciones de Typer ordenadas; docstrings completados
- `build.py` movido a `scripts/`

## [0.1.0] – 0.5.0 (alfa 1 → alfa 5) - 2026-08-01 → 2026-08-15

### Añadido
- CLI con Typer y carga de `config.toml`
- Comandos iniciales: `transcode`, `rotate`, `gif`, `concat` (demux y concat filter)
- Sistema de logging y sistema de errores estandarizado
- Validación del fichero de configuración
- Resolución de conflictos de salida (skip/overwrite)
- Aplicación multilenguaje (alfa 5: francés, italiano, alemán)
- Suite de tests inicial (generador de vídeos de prueba, tests de comandos,
  script de testeo en masa)

### Corregido
- Bugs críticos de concat, crop, reescalado y validación de extensiones
- Barra de progreso para comandos ffmpeg
- `encode` en masa continúa tras conflicto con `SKIP`
