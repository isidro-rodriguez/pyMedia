# Changelog

Formato esquemático basado en [Keep a Changelog](https://keepachangelog.com/).
Las versiones se han reconstruido a partir del histórico de
`src/pymedia/__init__.py` (el repositorio no usa tags de git).
Las versiones intermedias no registradas (0.2–0.4, 0.6–0.8) se agrupan
con la sección anterior.

## [0.14.0-beta.0] - 2026-09-11 → presente

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
