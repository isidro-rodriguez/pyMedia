Cli = {
    "concat_help": "Concatena i video nellordine specificato.",
    "crop_help": "Rifila il numero di pixel specificato.",
    "debug_help": "Livello di log DEBUG.",
    "encode_help": "Transcodifica utilizzando le opzioni selezionate (richiede almeno unopzione).",
    "end_point_help": "Punto temporale in cui termina la creazione della GIF.",
    "fps_help": "Fotogrammi al secondo della GIF animata.",
    "gif_help": "Genera una GIF animata dal video specificato.",
    "gyrate_help": "Ruota il file multimediale dellangolo specificato in gradi.",
    "invalid_path": "Non è un file: {path}",
    "output_help": "Nome del file di output.",
    "output_on_conflict_help": "Azione da intraprendere se esiste già un file con lo stesso nome.",
    "path_argument_help": "Video da elaborare.",
    "paths_argument_help": "Elenco di video da elaborare.",
    "remux_help": "Ricodifica utilizzando il profilo specificato nella configurazione.",
    "scale_gif_help": "Ridimensiona il file multimediale proporzionalmente allaltezza specificata.",
    "scale_video_help": "Ridimensiona il file multimediale proporzionalmente allaltezza specificata.",
    "show_help": "Mostra questo messaggio ed esce.",
    "split_help": "Divide un video nei punti specificati.",
    "start_point_help": "Punto temporale in cui inizia la creazione della GIF.",
    "trim_points_help": "Punti di taglio per il video.",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nImpostazione di configurazione non valida: encode.audio_bit_rate deve essere uno tra: {expected}",
    "invalid_audio_codec": "\nImpostazione di configurazione non valida: encode.audio_codec deve essere uno tra: {expected}",
    "invalid_channels": "\nImpostazione di configurazione non valida: conflictive_join.channels deve essere uno tra: {expected}",
    "invalid_default_container": "\nImpostazione di configurazione non valida: encode.default_container deve essere uno tra: {expected}",
    "invalid_fps": "\nImpostazione di configurazione non valida: conflictive_join.fps deve essere uno tra: {expected}",
    "invalid_language": "\nImpostazione di configurazione non valida: app.language deve essere uno tra: {expected}",
    "invalid_resize_to": "\nImpostazione di configurazione non valida: conflictive_join.resize_to deve essere uno tra: {expected}",
    "invalid_video_codec": "\nImpostazione di configurazione non valida: encode.video_codec deve essere uno tra: {expected}",
    "invalid_video_crf": "\nImpostazione di configurazione non valida: encode.video_crf deve essere compreso tra {min} e {max}",
    "invalid_video_preset": "\nImpostazione di configurazione non valida: encode.video_preset deve essere uno tra: {expected}",
}


Debug = {
    "ffmpeg_command": "Comando FFmpeg: {cmd}",
    "ffprobe_data": "Dati ffprobe: {data}",
    "pipeline_crop": "Ritaglio calcolato: {crop}",
    "pipeline_gyrate": "Rotazione applicata: {gyrate}",
    "pipeline_scale": "Scala calcolata: {scale}",
    "pipeline_time": "Tempo elaborato: {time}",
    "pipeline_trim": "Punti di taglio: {trim}",
}


ExecutionError = {
    "cannot_create_directory": "Impossibile creare la cartella: {path}",
    "command_execution": "Il comando FFmpeg {command_name} è fallito durante lesecuzione. Errore: {error}",
    "command_generation": "Il comando FFmpeg {command_name} non è stato generato.",
    "ffmpeg_timeout": "Loperazione FFmpeg ha superato il tempo limite consentito.",
    "invalid_config": "Configurazione non valida: {message}",
    "invalid_config_setting": "Impostazione di configurazione non valida: {setting} deve essere {expected}",
    "missing_config_section": "Sezione di configurazione mancante: {section}",
    "missing_config_setting": "Impostazione di configurazione mancante: {setting}",
    "unexpected_config_setting": "Impostazione di configurazione non prevista: {setting}",
}


Info = {
    "config_saved": "Salvataggio di config.toml",
    "concat_success": "Video concatenati con successo: {output}",
    "encode_success": "Transcodifica completata con successo: {output}",
    "gif_success": "GIF generata con successo: {output}",
    "split_success": "Video diviso con successo: {output}",
}


PipelineError = {
    "incompatible_files": "I file video non sono compatibili tra loro.",
    "missing_arguments": "Argomenti mancanti recuperati da Typer.",
    "missing_argument": "Argomento mancante: {argument}",
    "missing_media": "Impossibile trovare le informazioni multimediali per {path}.",
    "missing_media_property": "Impossibile trovare la proprietà multimediale {property_name}.",
    "output_on_conflict": "Processo interrotto perché il file di output esiste già.",
}


Progress = {
    "concat": "Concatenazione in corso",
    "encode": "Transcodifica in corso",
    "gif": "Generazione GIF in corso",
    "split": "Divisione in corso",
}


ValidationError = {
    "crop_all_zero": "Ritaglio non valido: tutti i valori sono 0.",
    "crop_exceeds_height": "Ritaglio non valido: {total} >= altezza originale {height}.",
    "crop_exceeds_width": "Ritaglio non valido: {total} >= larghezza originale {width}.",
    "insufficient_inputs": "Devono essere forniti almeno due video per questo comando.",
    "invalid_crop_format": "Formato di ritaglio non valido. Atteso: LEFT,RIGHT,TOP,BOTTOM.",
    "invalid_directory_name": '{directory} contiene caratteri non validi: < > : " / \\ | ? *',
    "invalid_extension": "Estensione {extension} non valida. Il codec {codec} richiede uno tra: {supported}.",
    "invalid_filename": '{filename} contiene caratteri non validi: < > : " / \\ | ? *',
    "invalid_gif_extension": "Estensione {extension} non valida. Le immagini GIF richiedono il contenitore .gif.",
    "invalid_gyrate": "Formato di rotazione non valido. Atteso: 90 | 180 | 270.",
    "invalid_setting": "Impostazione non valida: {parameter}",
    "invalid_time_format": "Formato timestamp non valido. Atteso: hh:mm:ss.",
    "invalid_trim_points": "Punti di taglio non validi.",
    "invalid_video_extension": "Estensione video {extension} non valida. I file video richiedono uno tra: {supported}.",
    "missing_options": "È richiesta almeno unopzione.",
    "negative_time": "Il timestamp non può essere negativo.",
    "time_exceeds_duration": "Il timestamp {time} supera la durata del video {duration}.",
}


Warnings = {
    "missing_options": "È richiesta almeno unopzione.",
    "output_exist": "Il file esiste già: {file_path}.",
    "scale_rejected_equal": "Ridimensionamento rifiutato: {scale} = altezza originale {height}.",
    "scale_rejected_increase": "Ridimensionamento a {scale}p non applicato: la risoluzione è superiore a quella originale ({height}p).",
}
