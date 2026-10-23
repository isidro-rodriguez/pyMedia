# Comandos de subtítulos

Los subtítulos se copian sin recodificar cuando el contenedor lo permite. Los índices
de pista son los que muestra `info` (ver [Pistas e índices](../conceptos.md#pistas-e-índices)).

## `add-subs`

Añade un fichero de subtítulos como nueva pista.

```bash
pymedia add-subs pelicula.mkv subs_en.srt --language eng
pymedia add-subs pelicula.mp4 subs_es.ass --language spa --title "Español"
```

| Argumento / opción    | Descripción                                                     |
|-----------------------|-----------------------------------------------------------------|
| `MEDIA_FILE`          | Vídeo de destino.                                               |
| `SUBTITLES_FILE`      | Fichero `.srt`, `.ass` o `.ssa`.                                |
| `--language`          | **Obligatorio.** Idioma de la pista.                            |
| `--title`             | Título visible. Por defecto, el nombre nativo del idioma.       |
| `--strip-disposition` | No copia los metadatos del origen.           |
| `-o`, `-ov`           | Ver [opciones comunes](../conceptos.md#opciones-comunes).       |

- ffprobe comprueba que el fichero es realmente de subtítulos y que su formato
  corresponde a la extensión.
- La pista se añade al final y **sin disposiciones**. Márcala después con
  `edit-subs --default` o `--forced`.
- El códec de la pista se elige según el contenedor de salida:

| Contenedor de salida        | Códec       |
|-----------------------------|-------------|
| `.mkv`                      | `srt`       |
| `.mp4`, `.mov`, `.m2ts`, `.ts` | `mov_text` |
| `.webm`                     | `webvtt`    |

!!! warning "Se pierden los estilos"
    Al convertir `.ass`/`.ssa` a `srt` o `mov_text` se pierden los estilos (posición,
    colores, fuentes). Usa `.mkv` para conservarlos.

## `delete-subs`

Elimina pistas de subtítulos.

```bash
pymedia delete-subs pelicula.mkv --tracks 3,4,5
```

| Opción      | Descripción                                           |
|-------------|-------------------------------------------------------|
| `--tracks`  | **Obligatorio.** Índices de las pistas que eliminar.  |
| `-o`, `-ov` | Ver [opciones comunes](../conceptos.md#opciones-comunes). |

## `edit-subs`

Cambia los metadatos y las disposiciones de una pista de subtítulos.

```bash
pymedia edit-subs pelicula.mkv --track 2 --language eng
pymedia edit-subs pelicula.mkv --track 2 --title "Español (forzados)" --default --forced
```

| Opción                                         | Descripción                                               |
|------------------------------------------------|-----------------------------------------------------------|
| `--track`                                      | **Obligatorio.** Índice de la pista.                      |
| `--language`                                   | Idioma (mismos formatos que en [`edit-audio`](audio.md#edit-audio)). |
| `--title`                                      | Título visible.                                           |
| `--default` / `--no-default`                   | Pista predeterminada (exclusiva entre subtítulos).        |
| `--forced` / `--no-forced`                     | Pista forzada: el reproductor la muestra siempre.         |
| `--hearing-impaired` / `--no-hearing-impaired` | Para personas con discapacidad auditiva (SDH).            |
| `--visual-impaired` / `--no-visual-impaired`   | Para personas con discapacidad visual.                    |
| `-o`, `-ov`                                    | Ver [opciones comunes](../conceptos.md#opciones-comunes). |

Las disposiciones que no indiques se conservan.

## `extract-subs`

Extrae pistas de subtítulos a ficheros independientes.

```bash
pymedia extract-subs pelicula.mkv --tracks 0
pymedia extract-subs pelicula.mkv --tracks 3,5 -o subs.srt
```

| Opción                | Descripción                                              |
|-----------------------|----------------------------------------------------------|
| `--tracks`            | **Obligatorio.** Índices de las pistas que extraer.      |
| `--strip-disposition` | No copia los metadatos del origen.                     |
| `-o`, `-ov`           | Ver [opciones comunes](../conceptos.md#opciones-comunes). |

- Se genera un fichero por pista: `<nombre>_subtitles_track_<N>.<ext>`.
- La extensión por defecto es `default_containers.subtitles` (`.srt`).
- Los subtítulos gráficos (PGS de Blu-ray, VobSub de DVD) no son texto y no pueden
  extraerse a `.srt`: el error indica los contenedores válidos (normalmente `.mkv`).
