# Changelog

Formato esquemático basado en [Keep a Changelog](https://keepachangelog.com/).
Las versiones se han reconstruido a partir del histórico de
`src/pymedia/__init__.py` (el repositorio no usa tags de git).
Las versiones intermedias no registradas (0.2–0.4, 0.6–0.8) se agrupan
con la sección anterior.

## [0.20.1-beta.11] - 2026-09-24

### Añadido

- `feat(locales)`: la variable de entorno `PYMEDIA_LANG` fuerza el idioma de la
  interfaz (códigos ISO 639-2 `eng`/`spa`, los mismos que `--language`, o los
  nombres `english`/`spanish`) con prioridad sobre `app.language` de
  `config.toml` y sobre el idioma del sistema; al resolverse antes de importar
  la aplicación también afecta a los textos de ayuda, y los valores desconocidos
  se ignoran

### Cambiado

- `chore(types)`: pyright en modo estricto sobre `src/` como dependencia de
  desarrollo, hook de pre-commit y tareas de VS Code; tipado explícito en
  `models/config.py` y en los comandos `scene` y `sheet`
- `refactor(main)`: `_configure_runtime()` y `_build_app()` sustituyen a los
  imports diferidos con `# ruff: noqa: E402`
- `docs`: README y página man documentan `PYMEDIA_LANG`

### Corregido

- `fix(tests)`: el idioma base (`en`) se fija en `tests/conftest.py` antes de
  importar la aplicación, por lo que los tests dejan de depender del idioma de
  la máquina (`test_main_help[cli]`)

## [0.20.0-beta.10] - 2026-09-22

### Añadido

- `feat(info)`: mejorada la visualización de metadatos en la tabla de información con columnas compactas y abreviadas (`Sample`, `Lang`, `Def`, `For`, `HI`, `Com`, `VI`)
- `test`: ampliada significativamente la cobertura de pruebas para comandos y formatos (tests de CLI, opciones y fixtures de compatibilidad)

### Cambiado

- `refactor(tests)`: reestructurada la suite de pruebas completa con mejor soporte para binarios y fixtures centralizados (`scripts/fixtures/`)
- `refactor(core)`: limpiadas importaciones y mejoradas validaciones de comandos en `base_service.py` y `base_cli_options.py`
- `refactor(fixtures)`: reorganizado y centralizado el sistema de generación de archivos de prueba
- `chore(config)`: eliminada configuración de mypy y actualizado `.gitignore`
- `docs`: actualizado README a versión 0.20.0

### Corregido

- `fix(i18n)`: corregidos msgids obsoletos en POT (`%(bit_rate)s bps`, `Sample rate`, `Forced`, `Default`) que no existían en código fuente; regenerados `pymedia.pot`, `es.po` y `es.mo`
- `fix(locales)`: todos los msgids del POT ahora se usan en `src/` (test `test_all_pot_msgids_used_in_src` pasa)

## [0.19.2-beta.9] - 2026-09-20

### Añadido

- `feat(cli)`: validación especializada por tipo de medio en comandos con listado de entradas (`transcode`, `sheet`, `join`)
- `feat(remux)`: mejoras en la gestión de pistas y compatibilidad de subtítulos
- `feat(commands)`: parámetros de configuración exclusiva integrados en comandos de audio (`add-audio`) y subtítulos (`add-subs`)

### Cambiado

- `chore`: mejorados mensajes de localización
- `refactor(cli)`: mejorada la validación de opciones requeridas y tipos de argumentos en comandos de edición de audio y subtítulos
- `refactor(join)`: reordenada la validación de compatibilidad de medios, eliminando comprobación redundante de `format_name`
- `docs`: documentación, localización y configuración del proyecto actualizadas (README, `pyproject.toml`, páginas de ayuda)
- `chore`: corrección de tipado, mejora del etiquetado en pistas de audio y subtítulos, actualización de tests

### Corregido

- `fix(core)`: mejorada la validación de marcas de tiempo y consistencia de extensiones
- `fix`: corrección a los mensajes de entradas de marcas de tiempo incorrectas
- `fix`: aplicación de la misma política `overwrite` a comandos de imágenes (`frames`, `interval`, `scene`)

## [0.19.1-beta.9] - 2026-09-20

### Cambiado

- Script de compilación renombrado de `build_windows.py` a `build.py`
  con soporte multiplataforma (Windows/Linux/macOS); genera
  `build/pymedia.exe` en Windows y `build/pymedia` en Unix.
- Tests E2E del binario adaptados a la nueva ruta y nombre del script
  de compilación, con detección automática de plataforma.
- Fixture de pistas de audio: directorio de salida simplificado a
  `fixtures/` relativo y creación recursiva con `parents=True`.

### Corregido

- La salida ya no puede coincidir con un fichero de entrada (antes `remux`/`cut`
  con `-o` igual a la entrada borraban el original al fallar ffmpeg)
- `transcode` conserva los subtítulos (a `mov_text` en MP4; los gráficos se
  descartan) y mantiene el orden vídeo, audio, subtítulos
- `join` copia todas las pistas (`-map 0`) y cita siempre las rutas del listado
- ffmpeg se lanza con `-nostdin` y `-y`/`-n` según la política `--overwrite`:
  `no` y `ask` ya no cuelgan hasta el `stall_timeout`
- `frames`: ruta de salida real (protección de sobrescritura y mensajes) y
  aviso si no se captura ningún fotograma
- `scene`: regex de capturas existentes (`\d{3}` en f-string), valor por
  defecto `--scene 0.3` y aviso si no hay cambios de escena
- `interval`: nombres esperados `_001…`, `--every` obligatorio y >= 1
- `FfprobeError` es un error de usuario (sin traceback ni banner de ffprobe) y
  se avisa si ffmpeg/ffprobe no están en el `PATH`
- Detección de idioma con precedencia POSIX (`LANGUAGE > LC_ALL > LC_MESSAGES >
  LANG`)
- `cut` informa del número correcto de ficheros; textos y ejemplos de ayuda
  corregidos; mensaje de sobrescritura traducible

### Interno

- `.gitignore`: añadidos directorios `.kilo/` y `.vscode/`.

## [0.18.0-beta.8] - 2026-09-19

### Añadido

- Soporte de salida APNG y WEBP animado en el comando `animated`, con
  opciones por contenedor (`apng`: compresión 9 y reproducción infinita;
  `webp`: `libwebp_anim` con pérdida, calidad 80 y bucle infinito;
  `gif`: `-loop 0`)
- Enum `ScaleFlag` con los modos de redimensionado de filtros ffmpeg
  (`fast_bilinear`, `bilinear`, `bicubic`, `area`, `lanczos`, `spline`,
  `neighbor`)
- Rotación diaria del log con `TimedRotatingFileHandler`: rotación a
  medianoche, conservando los últimos 7 días como ficheros con sufijo
  de fecha (`%Y-%m-%d`)

### Cambiado

- El redimensionado en `animated` usa el filtro `scale` con
  `flags=lanczos` para mayor calidad
- `animated` genera la paleta del APNG con `palettegen
  max_colors=256:stats_mode=diff` y dithering `sierra2_4a` (antes solo
  se optimizaba la paleta del GIF)
- `ScaleMixin.to_scale_cmd` y `FiltersMixin.to_filters_cmd` aceptan un
  `scale_flag` opcional para añadir los flags de redimensionado al filtro
- Logger: los valores interpolados en los mensajes (`%s`) se convierten
  a texto y se escapan del markup de Rich, evitando errores de
  renderizado con ficheros/paths que contienen corchetes

## [0.17.0-beta.7] - 2026-09-18

### Cambiado

- Estructura de la CLI: el módulo `typer/` se disuelve en
  `commands/base_cli.py` (instancia y validadores),
  `commands/base_cli_options.py` (opciones) y `commands/main/cli.py`
  (callback principal); el punto de entrada pasa a `main_cli`
- Paquetes de subtítulos renombrados a nombres explícitos
  (`add_subs`→`add_subtitles`, `delete_subs`→`delete_subtitles`,
  `edit_subs`→`edit_subtitles`, `extract_subs`→`extract_subtitles`); los
  nombres de comando CLI no cambian
- `delete-audio`, `extract-audio`, `delete-subs` y `extract-subs` exigen
  indicar las pistas a manipular: eliminado el fallback "sin listado se
  aplica a todas las pistas" (`_resolve_tracks`)
- Ayudas de comandos actualizadas (consulta de pistas con `info`) y
  locales `es` regenerados y compilados (`pymedia.pot`/`.po`/`.mo`)
- Tests adaptados al nuevo comportamiento (`--tracks 0` + `Missing
  parameter: media.audio`/`media.subtitles`)
- Dependencia `platformdirs` 4.11.9 → 4.11.10

### Interno

- README: diagrama de arquitectura actualizado al flujo
  CLI → parámetros → servicio

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
- Tests E2E del binario PyInstaller integrados en la suite CLI (`tests/test_cli.py`, `tests/test_cli_options.py`)
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
