# Comandos de vídeo

| Comando     | Recodifica | Uso típico                                               |
|-------------|:----------:|----------------------------------------------------------|
| `transcode` | Sí         | Reducir tamaño, cambiar códec, aplicar filtros.          |
| `remux`     | No         | Cambiar de contenedor, reparar marcas de tiempo.         |
| `cut`       | No         | Recortar un tramo o dividir en partes.                   |
| `join`      | No         | Unir varios vídeos compatibles.                          |

Los comandos sin recodificación usan `-c copy`: son muy rápidos y no pierden calidad,
pero dependen de que el contenedor de destino admita los códecs de origen (ver
[Formatos](../formatos.md)).

## `transcode`

Recodifica el vídeo y/o el audio con uno de los perfiles de `config.toml`.

```bash
# Solo vídeo, perfil equilibrado
pymedia transcode entrada.mkv --video

# Vídeo y pistas de audio 0 y 1 con el perfil rápido
pymedia transcode entrada.mkv --preset fast --video --audio 0,1 -o salida.mp4

# Reducir a 720p y voltear (los filtros activan --video)
pymedia transcode entrada.mp4 --size 1280x720 --hflip

# Quemar subtítulos en la imagen
pymedia transcode entrada.mp4 --burn-subtitles subs.srt

# Lote completo a otro directorio
pymedia transcode *.mkv --preset slow --video -d salida/
```

| Opción              | Valores                   | Defecto       | Descripción                                          |
|---------------------|---------------------------|---------------|------------------------------------------------------|
| `--preset`          | `fast`, `even`, `slow`    | `even`        | Perfil de `config.toml`.                             |
| `--video`           | —                         | —             | Recodifica la pista de vídeo.                        |
| `--audio`           | `N,M,...`                 | —             | Pistas de audio a recodificar; el resto se copian.   |
| `--burn-subtitles`  | Ruta `.srt`/`.ass`/`.ssa` | —             | Dibuja los subtítulos en la imagen.                  |
| `--strip-disposition` | —                       | —             | No copia los metadatos del origen.                 |
| `-o`, `-d`, `-ov`   |                           |               | Ver [opciones comunes](../conceptos.md#opciones-comunes). |
| Filtros             |                           |               | `--crop`, `--size`, `--mode`, `--upscale`, `--rotate`, `--hflip`, `--vflip` ([Filtros](../filtros.md)). |

Debes indicar al menos una operación: `--video`, `--audio`, `--burn-subtitles` o un
filtro. Los filtros y `--burn-subtitles` implican recodificar el vídeo.

### Qué hace con cada pista

| Pista       | Comportamiento                                                                          |
|-------------|-----------------------------------------------------------------------------------------|
| Vídeo       | Con `--video` (o filtros), se recodifica con el códec, CRF y preset del perfil. Si no, se copia. |
| Audio       | Las pistas de `--audio` se recodifican con el códec y la tasa de bits del perfil; el resto se copian. |
| Subtítulos  | Se copian si el contenedor de salida los admite. Si no, pyMedia avisa: los de texto (SRT, ASS, WebVTT, mov_text) puede convertirlos al formato del contenedor (`mov_text` en MP4, `srt` en MKV, `webvtt` en WebM) si confirmas; los gráficos (PGS, VobSub) no se pueden convertir y se descartan. |

### Códecs del perfil

| `video_codec`     | Codificador   | Formato de píxel        | CRF    | Preset                          |
|-------------------|---------------|-------------------------|--------|---------------------------------|
| `h264`            | `libx264`     | `yuv420p` (8 bits)      | 0–51   | `ultrafast` … `placebo`         |
| `h265` / `hevc`   | `libx265`     | `yuv420p10le` (10 bits) | 0–51   | `ultrafast` … `placebo`         |
| `av1`             | `libsvtav1`   | `yuv420p10le` (10 bits) | 0–63   | `0` (lento) … `14` (rápido)     |

| `audio_codec` | Codificador | Tasas de bits admitidas                         |
|---------------|-------------|-------------------------------------------------|
| `aac`         | `aac`       | 96k, 128k, 160k, 192k, 224k, 256k, 320k          |
| `eac3`        | `eac3`      | 192k, 224k, 256k, 320k, 384k, 448k, 640k         |
| `opus`        | `libopus`   | 64k, 96k, 128k, 160k, 192k, 256k                 |

A menor CRF, más calidad y más tamaño. Un preset más lento comprime mejor con la misma
calidad, a cambio de tiempo.

En MP4, pyMedia añade `-movflags +faststart` para que el vídeo empiece a reproducirse
antes de descargarse por completo y, si el vídeo resultante es H.265, la etiqueta
`hvc1` que exigen los reproductores de Apple.

Ejemplo de aviso al pasar un MKV con subtítulos SRT a MP4:

```text
WARNING  Las pistas de subtítulos 0 (subrip) no son compatibles con .mp4.
¿Convertirlas a un formato de subtítulos compatible? [Y/n]:
```

Con `--show-cmd` no se pregunta y se muestra el comando con la conversión.

## `remux`

Cambia el contenedor sin recodificar y permite pequeñas reparaciones.

```bash
pymedia remux entrada.mp4 -o salida.mkv
pymedia remux entrada.mkv -o salida.mp4               # faststart automático
pymedia remux entrada.mp4 --genpts -o reparado.mkv
pymedia remux entrada.mkv --sort-tracks -o ordenado.mkv
pymedia remux movil.mp4 --rotate 90 -o girado.mp4
```

| Opción                | Valores               | Descripción                                                             |
|-----------------------|-----------------------|-------------------------------------------------------------------------|
| `-o`, `--output`      | `.mkv`, `.mp4`, `.webm` | **Obligatorio.** Fichero de salida.                                   |
| `--genpts`            | —                     | Regenera marcas de tiempo dañadas (errores de reproducción o de salto). |
| `--sort-tracks`       | —                     | Ordena las pistas por tipo (vídeo, audio, subtítulos) y, dentro de cada tipo, por código de idioma; las pistas sin idioma van al final en su orden original. |
| `--rotate`            | `0`, `90`, `180`, `270` | Gira la imagen mediante metadatos de orientación, sin recodificar.    |
| `--strip-disposition` | —                     | No copia los metadatos del origen.                                    |

- Se copian todas las pistas de vídeo, audio y subtítulos.
- Al pasar a MP4, los subtítulos se convierten a `mov_text`, se mueve el índice
  (`moov`) al principio del fichero (`faststart`) y el vídeo H.265 se etiqueta como
  `hvc1` para los reproductores de Apple.
- Antes de ejecutar, pyMedia comprueba que cada códec se puede copiar de forma segura
  al nuevo contenedor. Si no, el error indica los contenedores válidos y tendrás que
  usar `transcode`.

## `cut`

Recorta un tramo o divide el vídeo en partes, sin recodificar.

```bash
pymedia cut entrada.mp4 --start 00:30                    # desde 0:30 hasta el final
pymedia cut entrada.mp4 --end 10:00                      # desde el inicio hasta 10:00
pymedia cut entrada.mp4 --start 01:00 --end 1:30:00      # tramo intermedio
pymedia cut entrada.mp4 --at 10:05,40:30,1:20:00         # cuatro partes
```

| Opción                | Descripción                                                         |
|-----------------------|---------------------------------------------------------------------|
| `--start`             | Inicio del tramo.                                                   |
| `--end`               | Fin del tramo.                                                      |
| `--at`                | Lista de marcas en las que dividir. Excluyente con `--start`/`--end`. |
| `--strip-disposition` | No copia los metadatos del origen.                                |
| `-o`, `-ov`           | Ver [opciones comunes](../conceptos.md#opciones-comunes).           |

- Con `--at`, N marcas generan N + 1 ficheros: `<nombre>_split_000`, `_001`…
- **Precisión:** al no recodificar, ffmpeg solo puede cortar en fotogramas clave
  (_keyframes_). El corte real puede desplazarse unos segundos respecto a la marca;
  pyMedia lo avisa con un mensaje. Para cortes exactos, recorta y después usa
  `transcode`.

## `join`

Une varios vídeos en el orden indicado, sin recodificar, con el demuxer `concat` de
ffmpeg.

```bash
pymedia join parte1.mp4 parte2.mp4 parte3.mp4 -o completo.mp4
```

| Opción                | Descripción                                              |
|-----------------------|----------------------------------------------------------|
| `-o`, `--output`      | **Obligatorio.** Fichero de salida.                      |
| `--strip-disposition` | No copia los metadatos del origen.                     |
| `-ov`                 | Política de sobrescritura.                               |

Antes de unir, pyMedia compara cada vídeo con el primero y aborta con un informe de
diferencias si no son compatibles:

| Pista  | Debe coincidir                                                   |
|--------|------------------------------------------------------------------|
| Vídeo  | Presencia, códec, ancho, alto, fps y formato de píxel.           |
| Audio  | Presencia, número de pistas y, por pista, códec, frecuencia de muestreo, canales y disposición de canales. |

Si los vídeos no son compatibles, transcodifícalos primero con el mismo perfil y
tamaño (`transcode --video --audio ... --size ...`).
