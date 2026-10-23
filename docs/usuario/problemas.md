# Solución de problemas

## Cómo diagnosticar

1. **Mira el comando:** `--show-cmd` imprime el comando ffmpeg sin ejecutarlo. Puedes
   copiarlo y lanzarlo a mano para ver la salida completa de ffmpeg.
2. **Activa la depuración:** `--debug` muestra los datos de ffprobe, el comando y pide
   confirmación antes de ejecutarlo.
3. **Revisa el log:** `logging.log`, en el directorio de configuración (ver
   [Configuración](configuracion.md#ubicación)), guarda cada error con las últimas
   líneas de ffmpeg.
4. **Comprueba el fichero:** `pymedia info <fichero>` confirma pistas, códecs e
   índices.

## Errores frecuentes

### Instalación y entorno

| Mensaje                                                  | Causa y solución                                                       |
|----------------------------------------------------------|------------------------------------------------------------------------|
| `ffmpeg no se encontró en el PATH. Instala ffmpeg primero.` | Instala ffmpeg (ver [Instalación](instalacion.md)) y abre una terminal nueva. |
| `El fichero de configuración no es un TOML válido`       | Error de sintaxis en `config.toml`: revisa comillas y corchetes, o bórralo para regenerarlo. |
| `Configuración no válida: ...`                           | Un valor está fuera de rango. El mensaje lista cada clave y los valores admitidos. Ver [Validación](configuracion.md#validación). |
| Textos en otro idioma                                    | Fija el idioma con `app.language` o `PYMEDIA_LANG` (ver [Idioma](configuracion.md#idioma)). |

### Entradas

| Mensaje                                                  | Causa y solución                                                       |
|----------------------------------------------------------|------------------------------------------------------------------------|
| `Extensión .xxx no válida. Vídeo requiere una de: ...`   | La extensión no está en el catálogo de entradas (ver [Formatos](formatos.md#ficheros-de-entrada)). |
| `Contenedor de vídeo no válido`                          | El fichero no tiene pista de vídeo (por ejemplo, un `.mp4` solo de audio). |
| `ffprobe no pudo leer <fichero>`                         | Fichero dañado, incompleto o sin permisos de lectura.                  |
| `... no es un fichero de subtítulos reconocido`          | El contenido no corresponde a la extensión (p. ej. un `.srt` con otro formato). |
| `Índice de audio no incluido` / `Índice de subtítulos no incluido` | El índice no existe. Consulta los índices con `info`: empiezan en 0 y son por tipo. |

### Marcas de tiempo

| Mensaje                                                  | Causa y solución                                                       |
|----------------------------------------------------------|------------------------------------------------------------------------|
| `Formato de marca de tiempo no válido`                   | Usa `hh:mm:ss`, `mm:ss` o `ss`, sin espacios.                          |
| `La marca de tiempo ... supera la duración del vídeo`    | La marca es igual o posterior al final. Consulta la duración con `info`. |
| `La lista de marcas de tiempo debe estar en orden ascendente` | Ordena las marcas de `--at`.                                      |
| `Opciones ambiguas: no puedes combinar --at con --start o --end` | En `cut`, usa `--at` para dividir o `--start`/`--end` para recortar. |
| `El corte con remux puede ser impreciso` (aviso)         | Normal: el corte se ajusta al fotograma clave más cercano (ver [`cut`](comandos/video.md#cut)). |

### Salidas

| Mensaje                                                  | Causa y solución                                                       |
|----------------------------------------------------------|------------------------------------------------------------------------|
| `El fichero de salida debe ser distinto del de entrada`  | Indica otro nombre con `-o`. pyMedia nunca sobrescribe la entrada.     |
| `Proceso omitido porque el fichero de salida ya existe`  | Usaste `-ov no` o respondiste que no. Usa `-ov yes` para sobrescribir. |
| `Extensión ... no válida. El códec ... requiere una de: ...` | El contenedor de salida no admite el códec. Elige una de las extensiones listadas. |
| `No se puede hacer remux del códec ... a ...`            | La copia sin recodificar no es segura. Usa una extensión de la lista o `transcode`. |
| `Las dimensiones objetivo deben ser pares`               | En vídeo, `--size` necesita ancho y alto pares.                        |
| `Escala ignorada ... requiere ampliación` (aviso)        | El objetivo es mayor que el origen. Añade `--upscale` si quieres ampliar. |

### Ejecución de ffmpeg

| Mensaje                                                  | Causa y solución                                                       |
|----------------------------------------------------------|------------------------------------------------------------------------|
| `El comando FFmpeg falló durante la ejecución.`          | ffmpeg terminó con error. Debajo se muestran sus últimas líneas, que indican la causa real (códec no disponible, fichero dañado…). |
| `El comando FFmpeg ... agotó el tiempo de espera.`       | ffmpeg no dio señales de vida durante `stall_timeout` segundos. Sube el valor en `config.toml` si el proceso es lento pero legítimo. |
| `Comando FFmpeg ... interrumpido manualmente.`           | Pulsaste `Ctrl+C`. No queda ningún fichero a medias.                   |
| `Ficheros multimedia no compatibles para la salida de unión` | Los vídeos de `join` difieren en códec, resolución, fps o audio. El informe lista cada diferencia; iguálalos con `transcode`. |

## Preguntas frecuentes

**¿Se modifica alguna vez el fichero original?**
No. La salida siempre es un fichero distinto y se escribe en un temporal que solo se
mueve al destino cuando ffmpeg termina bien.

**¿Por qué `transcode` tarda tanto?**
H.265 y AV1 son lentos de codificar. Usa el perfil `fast` o un `video_preset` más
rápido en `config.toml`. `remux`, `cut` y `join` no recodifican y son casi
instantáneos.

**El MP4 resultante no se reproduce en un dispositivo concreto.**
Prueba con un perfil en `h264` + `aac`, la combinación más compatible.

**¿Cómo recupero la configuración original?**
Borra `config.toml`; se regenera en la siguiente ejecución.
