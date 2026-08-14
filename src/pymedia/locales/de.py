# ruff: noqa

Cli = {
    "concat_help": "Verbindet Videos in der angegebenen Reihenfolge",
    "crop_help": "Schneidet die angegebene Anzahl an Pixeln ab. [dim]Z. B.: -c 200,200,0,0[/dim]",
    "debug_help": "Log-Level DEBUG",
    "encode_help": "Transkodiert mit den ausgewählten Optionen (mindestens eine Option erforderlich)",
    "end_point_help": "Zeitpunkt, an dem die GIF-Erstellung endet. [dim]Z. B.: -ep 1:20[/dim]",
    "fps_help": "Bilder pro Sekunde des animierten GIFs. [dim]Z. B.: -f 12[/dim]",
    "gif_help": "Erstellt ein animiertes GIF aus dem angegebenen Video",
    "gyrate_help": "Dreht das Medium um den angegebenen Winkel in Grad. [dim]Z. B.: -g 90[/dim]",
    "invalid_path": "{path} ist keine Datei.",
    "output_help": "Name der Ausgabedatei. [dim]Z. B.: -o cut.mp4[/dim]",
    "output_on_conflict_help": "Aktion, die ausgeführt werden soll, wenn bereits eine Datei mit demselben Namen existiert. [dim]Z. B.: -oc rename[/dim]",
    "path_argument_help": "Zu verarbeitendes Video.",
    "paths_argument_help": "Liste der zu verarbeitenden Videos.",
    "remux_help": "Kodiert das Medium mit dem in der Konfiguration angegebenen Profil neu.",
    "scale_gif_help": "Ändert die Größe des Mediums proportional auf die angegebene Höhe. [dim]Z. B.: -s 240[/dim]",
    "scale_video_help": "Ändert die Größe des Mediums proportional auf die angegebene Höhe. [dim]Z. B.: -s 240[/dim]",
    "show_help": "Diese Meldung anzeigen und beenden.",
    "split_help": "Teilt ein Video an den angegebenen Zeitpunkten",
    "start_point_help": "Zeitpunkt, an dem die GIF-Erstellung beginnt. [dim]Z. B.: -sp 1:20[/dim]",
    "trim_points_help": "Trennpunkte für das Video. [dim]Z. B.: -t 00:10,00:20,00:30[/dim]",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nUngültige Konfigurationseinstellung: encode.audio_bit_rate muss einer der folgenden Werte sein: {expected}",
    "invalid_audio_codec": "\nUngültige Konfigurationseinstellung: encode.audio_codec muss einer der folgenden Werte sein: {expected}",
    "invalid_channels": "\nUngültige Konfigurationseinstellung: conflictive_join.channels muss einer der folgenden Werte sein: {expected}",
    "invalid_default_container": "\nUngültige Konfigurationseinstellung: encode.default_container muss einer der folgenden Werte sein: {expected}",
    "invalid_fps": "\nUngültige Konfigurationseinstellung: conflictive_join.fps muss einer der folgenden Werte sein: {expected}",
    "invalid_language": "\nUngültige Konfigurationseinstellung: app.language muss einer der folgenden Werte sein: {expected}",
    "invalid_resize_to": "\nUngültige Konfigurationseinstellung: conflictive_join.resize_to muss einer der folgenden Werte sein: {expected}",
    "invalid_video_codec": "\nUngültige Konfigurationseinstellung: encode.video_codec muss einer der folgenden Werte sein: {expected}",
    "invalid_video_crf": "\nUngültige Konfigurationseinstellung: encode.video_crf muss zwischen {min} und {max} liegen",
    "invalid_video_preset": "\nUngültige Konfigurationseinstellung: encode.video_preset muss einer der folgenden Werte sein: {expected}",
}


Debug = {
    "ffmpeg_command": "FFmpeg-Befehl: {cmd}",
    "ffprobe_data": "ffprobe-Daten: {data}",
    "pipeline_crop": "Berechneter Zuschnitt: {crop}",
    "pipeline_gyrate": "Angewendete Drehung: {gyrate}",
    "pipeline_scale": "Berechnete Skalierung: {scale}",
    "pipeline_time": "Verarbeitete Zeit: {time}",
    "pipeline_trim": "Trennpunkte: {trim}",
}


ExecutionError = {
    "cannot_create_directory": "Verzeichnis konnte nicht erstellt werden: {path}",
    "command_execution": "FFmpeg-Befehl '{command_name}' ist während der Ausführung fehlgeschlagen. Fehler: {error}",
    "command_generation": "FFmpeg-Befehl '{command_name}' wurde nicht erstellt.",
    "ffmpeg_timeout": "Der FFmpeg-Vorgang hat das zulässige Zeitlimit überschritten.",
    "invalid_config": "Ungültige Konfiguration: {message}",
    "invalid_config_setting": "Ungültige Konfigurationseinstellung: {setting} erwartet {expected}",
    "missing_config_section": "Fehlender Konfigurationsabschnitt: {section}",
    "missing_config_setting": "Fehlende Konfigurationseinstellung: {setting}",
    "unexpected_config_setting": "Unerwartete Konfigurationseinstellung: {setting}",
}


Info = {
    "config_saved": "config.toml wird gespeichert",
    "concat_success": "Videos erfolgreich verbunden: {output}",
    "encode_success": "Transkodierung erfolgreich abgeschlossen: {output}",
    "gif_success": "GIF erfolgreich erstellt: {output}",
    "split_success": "Video erfolgreich geteilt: {output}",
}


PipelineError = {
    "incompatible_files": "Die Videodateien sind nicht miteinander kompatibel.",
    "missing_arguments": "Aus Typer abgerufene Argumente fehlen.",
    "missing_argument": "Fehlendes Argument: {argument}",
    "missing_media": "Medieninformationen für '{path}' konnten nicht gefunden werden.",
    "missing_media_property": "Medieneigenschaft '{property_name}' konnte nicht gefunden werden.",
    "output_on_conflict": "Vorgang abgebrochen, da die Ausgabedatei bereits existiert.",
}


Progress = {
    "concat": "Verbinden",
    "encode": "Transkodieren",
    "gif": "GIF wird erstellt",
    "split": "Teilen",
}


ValidationError = {
    "crop_all_zero": "Ungültiger Zuschnitt: Alle Werte sind 0.",
    "crop_exceeds_height": "Ungültiger Zuschnitt: {total} >= ursprüngliche Höhe {height}.",
    "crop_exceeds_width": "Ungültiger Zuschnitt: {total} >= ursprüngliche Breite {width}.",
    "insufficient_inputs": "Für diesen Befehl müssen mindestens zwei Videos angegeben werden.",
    "invalid_crop_format": "Ungültiges Zuschnittsformat. Erwartet: LEFT,RIGHT,TOP,BOTTOM",
    "invalid_directory_name": "'{directory}' enthält ungültige Zeichen: '< > : \" / \\ | ? *'",
    "invalid_extension": "Ungültige Erweiterung '{extension}'. Der Codec '{codec}' erfordert eine der folgenden Erweiterungen: {supported}",
    "invalid_filename": "'{filename}' enthält ungültige Zeichen: '< > : \" / \\ | ? *'",
    "invalid_gyrate": "Ungültiges Drehformat. Erwartet: 90 | 180 | 270.",
    "invalid_time_format": "Ungültiges Zeitstempelformat. Erwartet: hh:mm:ss.",
    "invalid_trim_points": "Ungültige Trennpunkte.",
    "missing_options": "Mindestens eine Option ist erforderlich.",
    "negative_time": "Der Zeitstempel darf nicht negativ sein.",
    "time_exceeds_duration": "Der Zeitstempel {time} überschreitet die Videodauer {duration}.",
}


Warnings = {
    "missing_options": "Mindestens eine Option ist erforderlich.",
    "output_exist": "Datei existiert bereits: {file_path}",
    "scale_rejected_equal": "Skalierung abgelehnt: {scale} = ursprüngliche Höhe {height}.",
    "scale_rejected_increase": "Skalierung auf {scale}p nicht angewendet: Die Auflösung ist höher als die ursprüngliche Auflösung ({height}p).",
}
