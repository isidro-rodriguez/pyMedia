Cli = {
    "concat_help": "Fügt Videos in der angegebenen Reihenfolge zusammen.",
    "crop_help": "Schneidet die angegebene Anzahl an Pixeln zu.",
    "debug_help": "Meldungsstufe DEBUG.",
    "encode_help": "Transkodiert unter Verwendung der ausgewählten Optionen (erfordert mindestens eine Option).",
    "end_point_help": "Endzeitpunkt für die GIF-Erstellung.",
    "fps_help": "Bilder pro Sekunde (FPS) des animierten GIFs.",
    "gif_help": "Erstellt ein animiertes GIF aus dem angegebenen Video.",
    "gyrate_help": "Dreht das Medium um den angegebenen Winkel in Grad.",
    "invalid_path": "Keine Datei: {path}",
    "output_help": "Name der Ausgabedatei.",
    "output_on_conflict_help": "Aktion, die ausgeführt wird, wenn bereits eine Datei mit demselben Namen existiert.",
    "path_argument_help": "Zu verarbeitendes Video.",
    "paths_argument_help": "Liste der zu verarbeitenden Videos.",
    "remux_help": "Kodiert neu unter Verwendung des in der Konfiguration angegebenen Profils.",
    "scale_gif_help": "Skaliert das Medium proportional auf die angegebene Höhe.",
    "scale_video_help": "Skaliert das Medium proportional auf die angegebene Höhe.",
    "show_help": "Diese Nachricht anzeigen und beenden.",
    "split_help": "Teilt ein Video an den angegebenen Punkten.",
    "start_point_help": "Startzeitpunkt für die GIF-Erstellung.",
    "trim_points_help": "Schnittpunkte für das Video.",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nUngültige Konfigurationseinstellung: encode.audio_bit_rate muss eines der folgenden sein: {expected}",
    "invalid_audio_codec": "\nUngültige Konfigurationseinstellung: encode.audio_codec muss eines der folgenden sein: {expected}",
    "invalid_channels": "\nUngültige Konfigurationseinstellung: conflictive_join.channels muss eines der folgenden sein: {expected}",
    "invalid_default_container": "\nUngültige Konfigurationseinstellung: encode.default_container muss eines der folgenden sein: {expected}",
    "invalid_fps": "\nUngültige Konfigurationseinstellung: conflictive_join.fps muss eines der folgenden sein: {expected}",
    "invalid_language": "\nUngültige Konfigurationseinstellung: app.language muss eines der folgenden sein: {expected}",
    "invalid_resize_to": "\nUngültige Konfigurationseinstellung: conflictive_join.resize_to muss eines der folgenden sein: {expected}",
    "invalid_video_codec": "\nUngültige Konfigurationseinstellung: encode.video_codec muss eines der folgenden sein: {expected}",
    "invalid_video_crf": "\nUngültige Konfigurationseinstellung: encode.video_crf muss zwischen {min} und {max} liegen",
    "invalid_video_preset": "\nUngültige Konfigurationseinstellung: encode.video_preset muss eines der folgenden sein: {expected}",
}


Debug = {
    "ffmpeg_command": "FFmpeg-Befehl: {cmd}",
    "ffprobe_data": "ffprobe-Daten: {data}",
    "pipeline_crop": "Berechnetes Zuschneiden (Crop): {crop}",
    "pipeline_gyrate": "Angewendete Drehung: {gyrate}",
    "pipeline_scale": "Berechnete Skalierung: {scale}",
    "pipeline_time": "Verarbeitete Zeit: {time}",
    "pipeline_trim": "Schnittpunkte: {trim}",
}


ExecutionError = {
    "cannot_create_directory": "Verzeichnis konnte nicht erstellt werden: {path}",
    "command_execution": "FFmpeg-Befehl {command_name} ist während der Ausführung fehlgeschlagen. Fehler: {error}",
    "command_generation": "FFmpeg-Befehl {command_name} wurde nicht generiert.",
    "ffmpeg_timeout": "FFmpeg-Vorgang hat das zulässige Zeitlimit überschritten.",
    "invalid_config": "Ungültige Konfiguration: {message}",
    "invalid_config_setting": "Ungültige Konfigurationseinstellung: {setting} muss {expected} sein",
    "missing_config_section": "Fehlender Konfigurationsabschnitt: {section}",
    "missing_config_setting": "Fehlende Konfigurationseinstellung: {setting}",
    "unexpected_config_setting": "Unerwartete Konfigurationseinstellung: {setting}",
}


Info = {
    "config_saved": "Speichere config.toml",
    "concat_success": "Videos erfolgreich zusammengefügt: {output}",
    "encode_success": "Transkodierung erfolgreich abgeschlossen: {output}",
    "gif_success": "GIF erfolgreich erstellt: {output}",
    "split_success": "Video erfolgreich geteilt: {output}",
}


PipelineError = {
    "incompatible_files": "Videodateien sind zueinander inkompatibel.",
    "missing_arguments": "Von Typer abgerufene Argumente fehlen.",
    "missing_argument": "Fehlendes Argument: {argument}",
    "missing_media": "Medieninformationen für {path} konnten nicht gefunden werden.",
    "missing_media_property": "Medieneigenschaft {property_name} konnte nicht gefunden werden.",
    "output_on_conflict": "Vorgang gestoppt, da die Ausgabedatei bereits existiert.",
}


Progress = {
    "concat": "Zusammenfügen",
    "encode": "Transkodieren",
    "gif": "GIF wird erstellt",
    "split": "Teilen",
}


ValidationError = {
    "crop_all_zero": "Ungültiger Zuschnitt: Alle Werte sind 0.",
    "crop_exceeds_height": "Ungültiger Zuschnitt: {total} >= ursprüngliche Höhe {height}.",
    "crop_exceeds_width": "Ungültiger Zuschnitt: {total} >= ursprüngliche Breite {width}.",
    "insufficient_inputs": "Für diesen Befehl müssen mindestens zwei Videos angegeben werden.",
    "invalid_crop_format": "Ungültiges Zuschnittsformat. Erwartet: LEFT,RIGHT,TOP,BOTTOM.",
    "invalid_directory_name": '{directory} enthält ungültige Zeichen: < > : " / \\ | ? *',
    "invalid_extension": "Ungültige Dateiendung {extension}. Codec {codec} erfordert eine der folgenden: {supported}.",
    "invalid_filename": '{filename} enthält ungültige Zeichen: < > : " / \\ | ? *',
    "invalid_gif_extension": "Ungültige Dateiendung {extension}. GIF-Bilder erfordern das Dateiformat .gif.",
    "invalid_gyrate": "Ungültiges Drehungsformat. Erwartet: 90 | 180 | 270.",
    "invalid_setting": "Ungültige Einstellung: {parameter}",
    "invalid_time_format": "Ungültiges Zeitstempelformat. Erwartet: hh:mm:ss.",
    "invalid_trim_points": "Ungültige Schnittpunkte.",
    "invalid_video_extension": "Ungültige Videoendung {extension}. Videodateien erfordern eine der folgenden: {supported}.",
    "missing_options": "Mindestens eine Option ist erforderlich.",
    "negative_time": "Zeitstempel kann nicht negativ sein.",
    "time_exceeds_duration": "Zeitstempel {time} überschreitet die Videodauer {duration}.",
}


Warnings = {
    "missing_options": "Mindestens eine Option ist erforderlich.",
    "output_exist": "Datei existiert bereits: {file_path}.",
    "scale_rejected_equal": "Skalierung abgelehnt: {scale} = ursprüngliche Höhe {height}.",
    "scale_rejected_increase": "Skalierung auf {scale}p nicht angewendet: Die Auflösung ist höher als das Original ({height}p).",
}
