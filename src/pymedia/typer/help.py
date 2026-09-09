"""Textos de ayuda de los comandos de Typer.

Centraliza las cadenas que alimentan el parámetro `help=` de la aplicación
y de sus subcomandos. Se traducen con gettext al importar este módulo, de
modo que respetan el idioma activo.
"""

from pymedia.locales import _  # noqa

# =============================================================================
#  Ayuda global de la aplicación
# =============================================================================

MAIN_HELP = _(
    """\
Easy CLI for ffmpeg.

[bold]Examples[/bold]:
  Generate an animated GIF from a video:   
    > pymedia gif input.mp4
  Print GIF's help:     
    > pymedia gif --help
"""
)


# =============================================================================
#  Comando GIF
# =============================================================================

GIF_HELP = _(
    """\
Generates an animated GIF from the specified video.

[bold]Examples[/bold]:
  Convert a video to GIF:
    > pymedia gif input.mp4
  Convert a time range:
    > pymedia gif input.mp4 --start 00:00:05 --end 00:00:12
  Set size and frame rate:
    > pymedia gif input.mp4 --size 480x270 --fps 15
  Save to a specific file:
    > pymedia gif input.mp4 --output output.gif
"""
)


# =============================================================================
#  Comando info
# =============================================================================

INFO_HELP = _(
    """\
Shows information about a video.

[bold]Example[/bold]:
  Shows video's metadata:
    > pymedia info input.mp4
"""
)


# =============================================================================
#  Comando sheet
# =============================================================================

SHEET_HELP = _(
    """\
Generates a thumbnail grid sheet with media info header.

[bold]Examples[/bold]:
  Generate a vcs with default HD preset:
    > pymedia sheet input.mp4
  Generates a vcs with different preset and specified output:
    > pymedia sheet input.mp4 --preset fhd -o vcs.webp
"""
)


# =============================================================================
#  Familia de comandos de audio
# =============================================================================

AUDIO_ADD_HELP = _(
    """\
Add an audio track to a media file.

[bold]Examples[/bold]:
  Add english audio to a media container:
    > pymedia add-audio input.mp4 eng_audio.aac --language eng
  Add default commentary spanish audio with custom title: 
    > pymedia add-audio input.mp4 spa_audio.aac --language spa --title "Comentario director" --default --commentary
"""  # noqa
)


AUDIO_DELETE_HELP = _(
    """\
Delete audio tracks from a media file.

[bold]Examples[/bold]:
  Delete all audio tracks from a media file:
    > pymedia delete-audio input.mp4
  Delete a list of audio tracks from a media file: 
    > pymedia delete-audio input.mp4 --tracks 1,2
"""  # noqa
)


AUDIO_EDIT_HELP = _(
    """\
Edit audio track metadata from a media file.

[bold]Examples[/bold]:
  Edit language metadata of audio stream track 1 from a media container:
    > pymedia edit-audio input.mp4 --track 1 --language eng
  Edit multiple tags in a single call: 
    > pymedia edit-audio input.mp4 --track 1 --language spa --title "Comentario director" --default --commentary
"""  # noqa
)


AUDIO_EXTRACT_HELP = _(
    """\
Extract audio tracks from a media file.

[bold]Examples[/bold]:
  Extract all audio tracks from a media file:
    > pymedia extract-audio input.mp4
  Extract a list of audio tracks from a media file: 
    > pymedia extract-audio input.mp4 --tracks 1,2
  Extract audio tracks with custom output:
    > pymedia extract-audio input.mp4 --tracks 1,2 -o input-audio.aac
"""  # noqa
)


# =============================================================================
#  Familia de subtítulos
# =============================================================================

SUBTITLES_ADD_HELP = _(
    """\
Add subtitles to a media file.

[bold]Examples[/bold]:
  Add english subtitles to a media container:
    > pymedia add-subs input.mp4 eng_subs.srt --language eng
  Add default forced spanish subtitles with custom title: 
    > pymedia add-subs input.mp4 eng_subs.srt --language spa --title "Español (forced)" --default --forced
"""  # noqa
)


SUBTITLES_DELETE_HELP = _(
    """\
Delete subtitles from a media file.

[bold]Examples[/bold]:
  Delete all subtitles from a media file:
    > pymedia delete-subs input.mp4
  Delete a list of subtitles tracks from a media file: 
    > pymedia delete-subs input.mp4 --tracks 3,4,5
"""  # noqa
)


SUBTITLES_EDIT_HELP = _(
    """\
Edit subtitles metadata from a media file.

[bold]Examples[/bold]:
  Edit language metadata to subtitles stream track 2 from a media container:
    > pymedia edit-subs input.mp4 --track 2 --language eng
  Edit multiple tags in a single call: 
    > pymedia edit-subs input.mp4 --track 2 --language spa --title "Español (forced)" --default --forced
"""  # noqa
)


SUBTITLES_EXTRACT_HELP = _(
    """\
Extract subtitles from a media file.

[bold]Examples[/bold]:
  Extract all subtitles from a media file:
    > pymedia extract-subs input.mp4
  Extract a list of subtitles tracks from a media file: 
    > pymedia extract-subs input.mp4 --tracks 3,4,5
  Extract subtitles tracks with custom output:
    > pymedia extract-subs input.mp4 --tracks 3,5 -o input-subtitles.srt
"""  # noqa
)


# =============================================================================
#  Familia de comandos de captura de imágenes
# =============================================================================

THUMB_FRAMES_HELP = _(
    """\
Captures thumbnails at the specified timestamps.

[bold]Examples[/bold]:
  Capture a single thumbnail at a given time:
    > pymedia frames input.mp4 --at 00:01:30
  Capture thumbnails at several timestamps:
    > pymedia frames input.mp4 --at 00:01:30,00:05:15
  Save to a specific file:
    > pymedia frames input.mp4 --at 00:01:30 --output thumb.jpg
"""
)


THUMB_INTERVAL_HELP = _(
    """\
Captures thumbnails at regular intervals of the video.

[bold]Examples[/bold]:
  Capture a thumbnail every second:
    > pymedia interval input.mp4 --every 1
  Capture a thumbnail every 5 seconds within a time range:
    > pymedia interval input.mp4 --every 5 --start 00:00:10 --end 00:01:00
  Save to a specific file:
    > pymedia interval input.mp4 --every 5 --output thumb.jpg
"""
)


THUMB_SCENE_HELP = _(
    """\
Captures thumbnails at the scene changes detected in the video.

[bold]Examples[/bold]:
  Detect scene changes with default sensitivity:
    > pymedia scene input.mp4
  Adjust the scene-change sensitivity:
    > pymedia scene input.mp4 --scene 0.3
  Limit the search to a time range:
    > pymedia scene input.mp4 --start 00:00:05 --end 00:00:30
  Save to a specific file:
    > pymedia scene input.mp4 --output thumb.jpg
"""
)
