# Documentación de pyMedia

pyMedia es una CLI que traduce operaciones habituales sobre vídeo, audio y subtítulos
a comandos `ffmpeg` seguros: valida las entradas con `ffprobe`, compone el comando,
muestra una barra de progreso y solo escribe la salida cuando ffmpeg termina bien.

Esta documentación amplía el [README](../README.md). Está dividida en dos partes.

## Guía de usuario

| Documento                                          | Contenido                                                             |
|----------------------------------------------------|-----------------------------------------------------------------------|
| [Instalación](usuario/instalacion.md)              | Requisitos, instalación con `uv`, ejecutable único y autocompletado.  |
| [Conceptos básicos](usuario/conceptos.md)          | Pistas e índices, marcas de tiempo, salidas, sobrescritura y lotes.   |
| [Comandos de análisis](usuario/comandos/analisis.md)     | `info`, `sheet`.                                                |
| [Comandos de vídeo](usuario/comandos/video.md)           | `transcode`, `remux`, `cut`, `join`.                            |
| [Comandos de audio](usuario/comandos/audio.md)           | `add-audio`, `delete-audio`, `edit-audio`, `extract-audio`.     |
| [Comandos de subtítulos](usuario/comandos/subtitulos.md) | `add-subs`, `delete-subs`, `edit-subs`, `extract-subs`.         |
| [Comandos de imagen](usuario/comandos/imagen.md)         | `animated`, `frames`, `interval`, `scene`.                      |
| [Filtros de imagen](usuario/filtros.md)            | `--crop`, `--size`, `--mode`, `--upscale`, `--rotate`, `--hflip/--vflip`. |
| [Configuración](usuario/configuracion.md)          | `config.toml`, validación, idioma, variables de entorno y logs.       |
| [Formatos y compatibilidad](usuario/formatos.md)   | Contenedores, códecs y qué combinaciones admite cada operación.       |
| [Solución de problemas](usuario/problemas.md)      | Errores frecuentes, diagnóstico con `--show-cmd` y `--debug`.         |

## Guía de desarrollo

| Documento                                          | Contenido                                                             |
|----------------------------------------------------|-----------------------------------------------------------------------|
| [Arquitectura](desarrollo/arquitectura.md)         | Capas, flujo de un comando, ejecución de ffmpeg, modelos y errores.   |
| [Añadir un comando](desarrollo/nuevo-comando.md)   | Receta paso a paso siguiendo la estructura del proyecto.              |
| [Contribuir](desarrollo/contribuir.md)             | Entorno, calidad, tests, traducciones, scripts, build y versionado.   |
