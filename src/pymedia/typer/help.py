"""Textos de ayuda de los comandos de Typer.

Centraliza las cadenas que alimentan el parámetro `help=` de la aplicación
y de sus subcomandos. Se traducen con gettext al importar este módulo, de
modo que respetan el idioma activo.
"""

from pymedia.locales import _  # noqa

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

ANIMATED_HELP = _(
    """\
Generates an animated image from the specified video.

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

INFO_HELP = _(
    """\
Shows information about a video.

[bold]Example[/bold]:
  Shows video's metadata:
    > pymedia info input.mp4
"""
)

JOIN_HELP = _(
    """\
Concatenate different videos into a single media container.

[bold]Example[/bold]:
  Join videos in the specified order:
    > pymedia join input1.mp4 input2.mp4 input3.mp4 -o output.mp4
"""
)

MAIN_HELP = _(
    """\
Easy CLI for ffmpeg.

[bold]Examples[/bold]:
  Show help and exit:
    > pymedia --help
    > pymedia
  Show subcommand help and exit:
    > pymedia transcode --help
    > pymedia transcode
"""
)

REMUX_HELP = _(
    """\
Change container and metadata without transcoding.

[bold]Examples[/bold]:
  Change video container:
    > pymedia remux input.mp4 -o output.mkv
  Fix faststart moving moov atom at the start 
    > pymedia remux input.mp4 --faststart -o output.mkv 
  Fix broken timestamps
    > pymedia remux input.mp4 --getpts -o output.mkv
  Sort stream tracks
    > pymedia remux input.mp4 --sort-tracks -o output.mp4
"""
)

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

SPLIT_HELP = _(
    """\
Split a video container in different media files.

[bold]Examples[/bold]:
  Split a media file at specific timestamps:
    > pymedia split input.mp4 --at 10:05,40:30,1:20:00
  Split a media file and remux container:
    > pymedia split input.mp4 --at 5:00 -o output.mkv
"""  # noqa
)

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

TRANSCODE_HELP = _(
    """\
Transcode video container changing its codecs and compression.

You can edit preset profiles in config.toml.

[bold]Examples[/bold]:
    Transcode only video track changing with a configurated profile:
    > pymedia transcode source.mp4 --profile balanced --video -o target.mp4
    Transcode video and audio track 1 changing its codecs with a configurated profile:
    > pymedia transcode source.mp4 --profile slow --video --audio 1 -o target.mp4
    Transcode video track meanwhile its applied multiple filters: 
    > pymedia transcode source.mp4 --profile fast --size 1280x720 --hflip
"""
)
