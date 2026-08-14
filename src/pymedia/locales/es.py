# ruff: noqa

Cli = {
    "concat_help": "Concatena vídeos en el orden especificado",
    "crop_help": "Recorta el número de píxeles especificado. [dim]E.g.: -c 200,200,0,0[/dim]",
    "debug_help": "Nivel de log DEBUG",
    "encode_help": "Transcodifica usando las opciones seleccionadas (requiere al menos una opción)",
    "end_point_help": "Punto de tiempo en el que termina la generación del GIF. [dim]E.g.: -ep 1:20[/dim]",
    "fps_help": "Fotogramas por segundo del GIF animado. [dim]E.g.: -f 12[/dim]",
    "gif_help": "Genera un GIF animado a partir del vídeo especificado",
    "gyrate_help": "Rota el medio por el ángulo especificado en grados. [dim]E.g.: -g 90[/dim]",
    "invalid_path": "{path} no es un archivo.",
    "output_help": "Nombre del archivo de salida. [dim]E.g.: -o cut.mp4[/dim]",
    "output_on_conflict_help": "Acción a tomar si ya existe un archivo con el mismo nombre. [dim]E.g.: -oc rename[/dim]",
    "path_argument_help": "Vídeo a procesar.",
    "paths_argument_help": "Lista de vídeos a procesar.",
    "remux_help": "Re-codifica usando el perfil especificado en la configuración.",
    "scale_gif_help": "Redimensiona el medio proporcionalmente a la altura especificada. [dim]E.g.: -s 240[/dim]",
    "scale_video_help": "Redimensiona el medio proporcionalmente a la altura especificada. [dim]E.g.: -s 240[/dim]",
    "show_help": "Muestra este mensaje y sale.",
    "split_help": "Divide un vídeo en los puntos especificados",
    "start_point_help": "Punto de tiempo en el que comienza la generación del GIF. [dim]E.g.: -sp 1:20[/dim]",
    "trim_points_help": "Puntos de división del vídeo. [dim]E.g.: -t 00:10,00:20,00:30[/dim]",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nConfiguración inválida: se espera que encode.audio_bit_rate sea uno de: {expected}",
    "invalid_audio_codec": "\nConfiguración inválida: se espera que encode.audio_codec sea uno de: {expected}",
    "invalid_channels": "\nConfiguración inválida: se espera que conflictive_join.channels sea uno de: {expected}",
    "invalid_default_container": "\nConfiguración inválida: se espera que encode.default_container sea uno de: {expected}",
    "invalid_fps": "\nConfiguración inválida: se espera que conflictive_join.fps sea uno de: {expected}",
    "invalid_language": "\nConfiguración inválida: se espera que app.language sea uno de: {expected}",
    "invalid_resize_to": "\nConfiguración inválida: se espera que conflictive_join.resize_to sea uno de: {expected}",
    "invalid_video_codec": "\nConfiguración inválida: se espera que encode.video_codec sea uno de: {expected}",
    "invalid_video_crf": "\nConfiguración inválida: se espera que encode.video_crf esté entre {min} y {max}",
    "invalid_video_preset": "\nConfiguración inválida: se espera que encode.video_preset sea uno de: {expected}",
}


Debug = {
    "ffmpeg_command": "Comando FFmpeg: {cmd}",
    "ffprobe_data": "Datos de ffprobe: {data}",
    "pipeline_crop": "Recorte calculado: {crop}",
    "pipeline_gyrate": "Rotación aplicada: {gyrate}",
    "pipeline_scale": "Escala calculada: {scale}",
    "pipeline_time": "Tiempo procesado: {time}",
    "pipeline_trim": "Puntos de división: {trim}",
}


ExecutionError = {
    "cannot_create_directory": "No se pudo crear el directorio: {path}",
    "command_execution": "El comando FFmpeg '{command_name}' falló durante la ejecución. Error: {error}",
    "command_generation": "El comando FFmpeg '{command_name}' no se generó.",
    "ffmpeg_timeout": "La operación FFmpeg superó el tiempo de espera permitido.",
    "invalid_config": "Configuración inválida: {message}",
    "invalid_config_setting": "Configuración inválida: se espera que {setting} sea {expected}",
    "missing_config_section": "Falta la sección de configuración: {section}",
    "missing_config_setting": "Falta la configuración: {setting}",
    "unexpected_config_setting": "Configuración inesperada: {setting}",
}


Info = {
    "config_saved": "Guardando config.toml",
    "concat_success": "Vídeos concatenados correctamente: {output}",
    "encode_success": "Transcodificación completada correctamente: {output}",
    "gif_success": "GIF generado correctamente: {output}",
    "split_success": "Vídeo dividido correctamente: {output}",
}


PipelineError = {
    "incompatible_files": "Los archivos de vídeo son incompatibles entre sí.",
    "missing_arguments": "Faltan argumentos recuperados de Typer.",
    "missing_argument": "Falta el argumento: {argument}",
    "missing_media": "No se pudo encontrar la información del medio para '{path}'.",
    "missing_media_property": "No se pudo encontrar la propiedad del medio '{property_name}'.",
    "output_on_conflict": "Proceso detenido porque el archivo de salida ya existe.",
}


Progress = {
    "concat": "Concatenando",
    "encode": "Transcodificando",
    "gif": "Generando GIF",
    "split": "Dividiendo",
}


ValidationError = {
    "crop_all_zero": "Recorte inválido: todos los valores son 0.",
    "crop_exceeds_height": "Recorte inválido: {total} >= altura original {height}.",
    "crop_exceeds_width": "Recorte inválido: {total} >= ancho original {width}.",
    "insufficient_inputs": "Se deben proporcionar al menos dos vídeos para este comando.",
    "invalid_crop_format": "Formato de recorte inválido. Esperado: IZQUIERDA,DERECHA,ARRIBA,ABAJO",
    "invalid_directory_name": "'{directory}' contiene caracteres inválidos: '< > : \" / \\ | ? *'",
    "invalid_extension": "Extensión '{extension}' inválida. El códec '{codec}' requiere uno de: {supported}",
    "invalid_filename": "'{filename}' contiene caracteres inválidos: '< > : \" / \\ | ? *'",
    "invalid_gyrate": "Formato de rotación inválido. Esperado: 90 | 180 | 270.",
    "invalid_time_format": "Formato de marca de tiempo inválido. Esperado: hh:mm:ss.",
    "invalid_trim_points": "Puntos de división inválidos.",
    "missing_options": "Se requiere al menos una opción.",
    "negative_time": "La marca de tiempo no puede ser negativa.",
    "time_exceeds_duration": "La marca de tiempo {time} supera la duración del vídeo {duration}.",
}


Warnings = {
    "missing_options": "Se requiere al menos una opción.",
    "output_exist": "El archivo ya existe: {file_path}",
    "scale_rejected_equal": "Escalado rechazado: {scale} = altura original {height}.",
    "scale_rejected_increase": "Escalado a {scale}p no aplicado: la resolución es mayor que la original ({height}p).",
}
