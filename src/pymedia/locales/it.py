# ruff: noqa

Cli = {
    "concat_help": "Concatena i video nell'ordine specificato",
    "crop_help": "Ritaglia il numero di pixel specificato. [dim]Es.: -c 200,200,0,0[/dim]",
    "debug_help": "Livello di log DEBUG",
    "encode_help": "Transcodifica utilizzando le opzioni selezionate (è richiesta almeno un'opzione)",
    "end_point_help": "Punto temporale in cui termina la generazione della GIF. [dim]Es.: -ep 1:20[/dim]",
    "fps_help": "Fotogrammi al secondo della GIF animata. [dim]Es.: -f 12[/dim]",
    "gif_help": "Genera una GIF animata dal video specificato",
    "gyrate_help": "Ruota il file multimediale dell'angolo specificato in gradi. [dim]Es.: -g 90[/dim]",
    "invalid_path": "{path} non è un file.",
    "output_help": "Nome del file di output. [dim]Es.: -o cut.mp4[/dim]",
    "output_on_conflict_help": "Azione da eseguire se esiste già un file con lo stesso nome. [dim]Es.: -oc rename[/dim]",
    "path_argument_help": "Video da elaborare.",
    "paths_argument_help": "Elenco di video da elaborare.",
    "remux_help": "Ricodifica utilizzando il profilo specificato nella configurazione.",
    "scale_gif_help": "Ridimensiona il file multimediale proporzionalmente all'altezza specificata. [dim]Es.: -s 240[/dim]",
    "scale_video_help": "Ridimensiona il video proporzionalmente all'altezza specificata. [dim]Es.: -s 240[/dim]",
    "show_help": "Mostra questo messaggio ed esce.",
    "split_help": "Divide un video nei punti specificati",
    "start_point_help": "Punto temporale in cui inizia la generazione della GIF. [dim]Es.: -sp 1:20[/dim]",
    "trim_points_help": "Punti di divisione del video. [dim]Es.: -t 00:10,00:20,00:30[/dim]",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nImpostazione di configurazione non valida: encode.audio_bit_rate deve essere uno dei seguenti valori: {expected}",
    "invalid_audio_codec": "\nImpostazione di configurazione non valida: encode.audio_codec deve essere uno dei seguenti valori: {expected}",
    "invalid_channels": "\nImpostazione di configurazione non valida: conflictive_join.channels deve essere uno dei seguenti valori: {expected}",
    "invalid_default_container": "\nImpostazione di configurazione non valida: encode.default_container deve essere uno dei seguenti valori: {expected}",
    "invalid_fps": "\nImpostazione di configurazione non valida: conflictive_join.fps deve essere uno dei seguenti valori: {expected}",
    "invalid_language": "\nImpostazione di configurazione non valida: app.language deve essere uno dei seguenti valori: {expected}",
    "invalid_resize_to": "\nImpostazione di configurazione non valida: conflictive_join.resize_to deve essere uno dei seguenti valori: {expected}",
    "invalid_video_codec": "\nImpostazione di configurazione non valida: encode.video_codec deve essere uno dei seguenti valori: {expected}",
    "invalid_video_crf": "\nImpostazione di configurazione non valida: encode.video_crf deve essere compreso tra {min} e {max}",
    "invalid_video_preset": "\nImpostazione di configurazione non valida: encode.video_preset deve essere uno dei seguenti valori: {expected}",
}


Debug = {
    "ffmpeg_command": "Comando FFmpeg: {cmd}",
    "ffprobe_data": "Dati ffprobe: {data}",
    "pipeline_crop": "Ritaglio calcolato: {crop}",
    "pipeline_gyrate": "Rotazione applicata: {gyrate}",
    "pipeline_scale": "Ridimensionamento calcolato: {scale}",
    "pipeline_time": "Tempo elaborato: {time}",
    "pipeline_trim": "Punti di divisione: {trim}",
}


ExecutionError = {
    "cannot_create_directory": "Impossibile creare la directory: {path}",
    "command_execution": "Il comando FFmpeg '{command_name}' non è riuscito durante l'esecuzione. Errore: {error}",
    "command_generation": "Il comando FFmpeg '{command_name}' non è stato generato.",
    "ffmpeg_timeout": "L'operazione FFmpeg ha superato il timeout consentito.",
    "invalid_config": "Configurazione non valida: {message}",
    "invalid_config_setting": "Impostazione di configurazione non valida: {setting} deve essere {expected}",
    "missing_config_section": "Sezione di configurazione mancante: {section}",
    "missing_config_setting": "Impostazione di configurazione mancante: {setting}",
    "unexpected_config_setting": "Impostazione di configurazione imprevista: {setting}",
}


Info = {
    "config_saved": "Salvataggio di config.toml",
    "concat_success": "Video concatenati correttamente: {output}",
    "encode_success": "Transcodifica completata correttamente: {output}",
    "gif_success": "GIF generata correttamente: {output}",
    "split_success": "Video diviso correttamente: {output}",
}


PipelineError = {
    "incompatible_files": "I file video non sono compatibili tra loro.",
    "missing_arguments": "Argomenti mancanti recuperati da Typer.",
    "missing_argument": "Argomento mancante: {argument}",
    "missing_media": "Non è stato possibile trovare le informazioni multimediali per '{path}'.",
    "missing_media_property": "Non è stato possibile trovare la proprietà multimediale '{property_name}'.",
    "output_on_conflict": "Processo interrotto perché il file di output esiste già.",
}


Progress = {
    "concat": "Concatenazione",
    "encode": "Transcodifica",
    "gif": "Generazione GIF",
    "split": "Divisione",
}


ValidationError = {
    "crop_all_zero": "Ritaglio non valido: tutti i valori sono 0.",
    "crop_exceeds_height": "Ritaglio non valido: {total} >= altezza originale {height}.",
    "crop_exceeds_width": "Ritaglio non valido: {total} >= larghezza originale {width}.",
    "insufficient_inputs": "È necessario fornire almeno due video per questo comando.",
    "invalid_crop_format": "Formato del ritaglio non valido. Previsto: LEFT,RIGHT,TOP,BOTTOM",
    "invalid_directory_name": "'{directory}' contiene caratteri non validi: '< > : \" / \\ | ? *'",
    "invalid_extension": "Estensione non valida '{extension}'. Il codec '{codec}' richiede una delle seguenti: {supported}",
    "invalid_filename": "'{filename}' contiene caratteri non validi: '< > : \" / \\ | ? *'",
    "invalid_gyrate": "Formato di rotazione non valido. Previsto: 90 | 180 | 270.",
    "invalid_time_format": "Formato del timestamp non valido. Previsto: hh:mm:ss.",
    "invalid_trim_points": "Punti di divisione non validi.",
    "missing_options": "È richiesta almeno un'opzione.",
    "negative_time": "Il timestamp non può essere negativo.",
    "time_exceeds_duration": "Il timestamp {time} supera la durata del video {duration}.",
}


Warnings = {
    "missing_options": "È richiesta almeno un'opzione.",
    "output_exist": "Il file esiste già: {file_path}",
    "scale_rejected_equal": "Ridimensionamento rifiutato: {scale} = altezza originale {height}.",
    "scale_rejected_increase": "Ridimensionamento a {scale}p non applicato: la risoluzione è superiore a quella originale ({height}p).",
}
