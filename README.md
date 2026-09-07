# pyMedia

Aplicación CLI que actúa como handler sencillo de comandos `ffmpeg` para tareas habituales de 
procesamiento de vídeos.

> Estado: **Alpha** (en pruebas locales).

## Requisitos

**Ffmpeg** y **ffprobe** instalados y disponibles en el `PATH`.
    
- Windows: `winget install ffmpeg` o <https://ffmpeg.org/download.html>
- Debian/Ubuntu: `sudo apt install ffmpeg`

## Configuración



### Compatibilidad entre códecs y contenedores de vídeo

|        | AV1 | H.264 | H.265 | AAC | E-AC-3 | Opus | ASS | SRT | SSA |
|--------|:---:|:-----:|:-----:|:---:|:------:|:----:|:---:|:---:|:---:|
| MKV    | ✓  |  ✓   |  ✓   | ✓  |   ✓   |  ✓  | ✓  | ✓  | ✓  |
| MP4    | ✓  |  ✓   |  ✓   | ✓  |   ✓   |      |     | ⚠  |     |
| WebM   | ✓  |       |       |     |        |  ✓  |     |     |     |

> ⚠ = Se transcodifica a `mov_text`

### Compatibilidad entre códes y contenedores de audio

|     | AAC | ALAC | FLAC | Opus | MP3 |
|-----|:---:|:----:|:----:|:----:|:---:|
| MKA | ✓  |  ✓  |  ✓  |  ✓  | ✓  |
| M4A | ✓  |  ✓  |      |  ⚠  |     |
| OGG |     |      |  ✓  |  ✓  | ⚠  |

> ⚠ = Soporte parcial/no universal, evitar si buscas compatibilidad amplia.

### Perfiles de transcodificación comunes

| Perfil       | Vídeo | CRF |  Preset  | Audio | Bit rate | Contenedor |
|:-------------|:-----:|:---:|:--------:|:------|---------:|:----------:|
| **fast**     | H264  | 21  | veryfast | AAC   | 192 kb/s |    MP4     |
| **balanced** | H265  | 22  |  medium  | Opus  | 112 kb/s |    MKV     |
| **slow**     |  AV1  | 24  |    7     | Opus  |  96 kb/s |    MKV     |

