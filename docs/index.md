---
title: Inicio
hide:
  - toc
---

<div class="pm-hero" markdown>

<div markdown>

# pyMedia

<p class="pm-hero__lead">
Analiza, corta, une, convierte y edita vídeos, pistas de audio y subtítulos con
comandos cortos y legibles, sin recordar la sintaxis de ffmpeg.
</p>

<p class="pm-hero__actions" markdown>
[Instalar pyMedia](usuario/instalacion.md){ .md-button .md-button--primary }
[Ver los comandos](usuario/comandos/analisis.md){ .md-button }
</p>

</div>

<div class="pm-terminal" role="figure" aria-label="Ejemplo de sesión: transcode de un MKV a MP4 con conversión de subtítulos">
<div class="pm-terminal__bar" aria-hidden="true"><span></span><span></span><span></span></div>
<pre><span class="p">$</span> <span class="c">pymedia</span> transcode pelicula.mkv <span class="f">--preset</span> fast <span class="f">--video</span>
<span class="w">▲</span> Las pistas de subtítulos <span class="v">0 (subrip)</span> no son compatibles con <span class="v">.mp4</span>.
<span class="q">?</span> <b>¿Convertirlas a un formato de subtítulos compatible?</b> <span class="b">[s/n]</span> <span class="m">(s)</span> s
<span class="ok">✔</span> Transcodificando el contenedor <span class="ok">━━━━━━━━━━━━━━━━━━━━━━━━</span> <span class="b">100%</span> <span class="m">•</span> <span class="m">0:42</span>
<span class="ok">✔</span> Contenedor transcodificado correctamente: <span class="v">pelicula_transcoded.mp4</span></pre>
</div>

</div>

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
