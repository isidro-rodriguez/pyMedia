Cli = {
    "concat_help": "Concatena videos en el orden especificado.",
    "crop_help": "Recorta el número especificado de píxeles.",
    "debug_help": "Nivel de registro DEBUG.",
    "encode_help": "Transcodifica usando las opciones seleccionadas (requiere al menos una opción).",
    "end_point_help": "Punto de tiempo en el que finaliza la generación del GIF.",
    "fps_help": "Fotogramas por segundo del GIF animado.",
    "gif_help": "Genera un GIF animado a partir del video especificado.",
    "gyrate_help": "Rota el archivo multimedia según el ángulo especificado en grados.",
    "invalid_path": "No es un archivo: {path}",
    "output_help": "Nombre del archivo de salida.",
    "output_on_conflict_help": "Acción a tomar si ya existe un archivo con el mismo nombre.",
    "path_argument_help": "Video a procesar.",
    "paths_argument_help": "Lista de videos a procesar.",
    "remux_help": "Vuelve a codificar utilizando el perfil especificado en la configuración.",
    "scale_gif_help": "Redimensiona el archivo multimedia proporcionalmente a la altura especificada.",
    "scale_video_help": "Redimensiona el archivo multimedia proporcionalmente a la altura especificada.",
    "show_help": "Muestra este mensaje y sale.",
    "split_help": "Divide un video en los puntos especificados.",
    "start_point_help": "Punto de tiempo en el que inicia la generación del GIF.",
    "trim_points_help": "Puntos de corte para el video.",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nAjuste de configuración no válido: encode.audio_bit_rate debe ser uno de: {expected}",
    "invalid_audio_codec": "\nAjuste de configuración no válido: encode.audio_codec debe ser uno de: {expected}",
    "invalid_channels": "\nAjuste de configuración no válido: conflictive_join.channels debe ser uno de: {expected}",
    "invalid_default_container": "\nAjuste de configuración no válido: encode.default_container debe ser uno de: {expected}",
    "invalid_fps": "\nAjuste de configuración no válido: conflictive_join.fps debe ser uno de: {expected}",
    "invalid_language": "\nAjuste de configuración no válido: app.language debe ser uno de: {expected}",
    "invalid_resize_to": "\nAjuste de configuración no válido: conflictive_join.resize_to debe ser uno de: {expected}",
    "invalid_video_codec": "\nAjuste de configuración no válido: encode.video_codec debe ser uno de: {expected}",
    "invalid_video_crf": "\nAjuste de configuración no válido: encode.video_crf debe estar entre {min} y {max}",
    "invalid_video_preset": "\nAjuste de configuración no válido: encode.video_preset debe ser uno de: {expected}",
}


Debug = {
    "ffmpeg_command": "Comando FFmpeg: {cmd}",
    "ffprobe_data": "Datos de ffprobe: {data}",
    "pipeline_crop": "Recorte calculado: {crop}",
    "pipeline_gyrate": "Rotación aplicada: {gyrate}",
    "pipeline_scale": "Escala calculada: {scale}",
    "pipeline_time": "Tiempo procesado: {time}",
    "pipeline_trim": "Puntos de corte: {trim}",
}


ExecutionError = {
    "cannot_create_directory": "No se pudo crear el directorio: {path}",
    "command_execution": "El comando FFmpeg {command_name} falló durante la ejecución. Error: {error}",
    "command_generation": "El comando FFmpeg {command_name} no fue generado.",
    "ffmpeg_timeout": "La operación de FFmpeg excedió el tiempo de espera permitido.",
    "invalid_config": "Configuración no válida: {message}",
    "invalid_config_setting": "Ajuste de configuración no válido: en {setting} se espera {expected}",
    "missing_config_section": "Falta la sección de configuración: {section}",
    "missing_config_setting": "Falta el ajuste de configuración: {setting}",
    "unexpected_config_setting": "Ajuste de configuración no esperado: {setting}",
}


Info = {
    "config_saved": "Guardando config.toml",
    "concat_success": "Videos concatenados correctamente: {output}",
    "encode_success": "Transcodificación completada correctamente: {output}",
    "gif_success": "GIF generado correctamente: {output}",
    "split_success": "Video dividido correctamente: {output}",
}


PipelineError = {
    "incompatible_files": "Los archivos de video son incompatibles entre sí.",
    "missing_arguments": "Faltan argumentos recuperados de Typer.",
    "missing_argument": "Falta el argumento: {argument}",
    "missing_media": "No se pudo encontrar la información multimedia para {path}.",
    "missing_media_property": "No se pudo encontrar la propiedad multimedia {property_name}.",
    "output_on_conflict": "Proceso detenido porque el archivo de salida ya existe.",
}


Progress = {
    "concat": "Concatenando",
    "encode": "Transcodificando",
    "gif": "Generando GIF",
    "split": "Dividiendo",
}


ValidationError = {
    "crop_all_zero": "Recorte no válido: todos los valores son 0.",
    "crop_exceeds_height": "Recorte no válido: {total} >= altura original {height}.",
    "crop_exceeds_width": "Recorte no válido: {total} >= ancho original {width}.",
    "insufficient_inputs": "Se deben proporcionar al menos dos videos para este comando.",
    "invalid_crop_format": "Formato de recorte no válido. Se esperaba: LEFT,RIGHT,TOP,BOTTOM.",
    "invalid_directory_name": '{directory} contiene caracteres no válidos: < > : " / \\ | ? *',
    "invalid_extension": "Extensión no válida {extension}. El códec {codec} requiere una de las siguientes: {supported}.",
    "invalid_filename": '{filename} contiene caracteres no válidos: < > : " / \\ | ? *',
    "invalid_gif_extension": "Extensión no válida {extension}. Las imágenes GIF requieren el contenedor .gif.",
    "invalid_gyrate": "Formato de rotación no válido. Se esperaba: 90 | 180 | 270.",
    "invalid_setting": "Ajuste no válido: {parameter}",
    "invalid_time_format": "Formato de marca de tiempo no válido. Se esperaba: hh:mm:ss.",
    "invalid_trim_points": "Puntos de corte no válidos.",
    "invalid_video_extension": "Extensión de video no válida {extension}. Los archivos de video requieren una de las siguientes: {supported}.",
    "missing_options": "Se requiere al menos una opción.",
    "negative_time": "La marca de tiempo no puede ser negativa.",
    "time_exceeds_duration": "La marca de tiempo {time} excede la duración del video {duration}.",
}


Warnings = {
    "missing_options": "Se requiere al menos una opción.",
    "output_exist": "El archivo ya existe: {file_path}.",
    "scale_rejected_equal": "Escalado rechazado: {scale} = altura original {height}.",
    "scale_rejected_increase": "No se aplicó el escalado a {scale}p: la resolución es mayor a la original ({height}p).",
}
