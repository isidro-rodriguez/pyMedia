---
template: home.html
title: pyMedia
hero:
  lead: >-
    Analiza, corta, une, convierte y edita vídeos, pistas de audio y subtítulos
    con comandos cortos y legibles, sin recordar la sintaxis de ffmpeg.
  actions:
    - title: Instalar pyMedia
      url: usuario/instalacion/
      primary: true
    - title: Ver los comandos
      url: usuario/comandos/analisis/
  images:
    - src: assets/images/sesion.svg
      alt: >-
        Ejemplo de sesión: transcode de un MKV a MP4 con conversión de subtítulos
---

pyMedia traduce operaciones habituales a comandos `ffmpeg` seguros: valida las
entradas con `ffprobe` antes de empezar, muestra el progreso y solo escribe la salida
cuando ffmpeg termina bien. El fichero original nunca se modifica.

## Guía de usuario

| Página                                                   | Contenido                                                                 |
|----------------------------------------------------------|---------------------------------------------------------------------------|
| [Instalación](usuario/instalacion.md)                    | Paquetes `.deb` y Windows, instalación desde el código y autocompletado.  |
| [Conceptos básicos](usuario/conceptos.md)                | Pistas e índices, marcas de tiempo, salidas, sobrescritura y lotes.       |
| [Comandos de análisis](usuario/comandos/analisis.md)     | `info`, `sheet`, `play`.                                                  |
| [Comandos de vídeo](usuario/comandos/video.md)           | `transcode`, `remux`, `cut`, `join`.                                      |
| [Comandos de audio](usuario/comandos/audio.md)           | `add-audio`, `delete-audio`, `edit-audio`, `extract-audio`.               |
| [Comandos de subtítulos](usuario/comandos/subtitulos.md) | `add-subs`, `delete-subs`, `edit-subs`, `extract-subs`.                   |
| [Comandos de imagen](usuario/comandos/imagen.md)         | `animated`, `frames`, `interval`, `scene`.                                |
| [Filtros de imagen](usuario/filtros.md)                  | `--crop`, `--size`, `--mode`, `--upscale`, `--rotate`, `--hflip/--vflip`. |
| [Configuración](usuario/configuracion.md)                | `config.toml`, validación, idioma, variables de entorno y logs.           |
| [Formatos y compatibilidad](usuario/formatos.md)         | Contenedores, códecs y qué combinaciones admite cada operación.           |
| [Solución de problemas](usuario/problemas.md)            | Errores frecuentes, diagnóstico con `--show-cmd` y `--debug`.             |

## Guía de desarrollo

| Página                                           | Contenido                                                               |
|--------------------------------------------------|-------------------------------------------------------------------------|
| [Arquitectura](desarrollo/arquitectura.md)       | Capas, flujo de un comando, ejecución de ffmpeg, interfaz, modelos y errores. |
| [Añadir un comando](desarrollo/nuevo-comando.md) | Receta paso a paso siguiendo la estructura del proyecto.                |
| [Contribuir](desarrollo/contribuir.md)           | Entorno, calidad, tests, traducciones, documentación, CI y versiones.   |

El código, los paquetes publicados y el historial de cambios están en el
[repositorio de GitHub](https://github.com/isidro-rodriguez/pyMedia).
