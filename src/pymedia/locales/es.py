Cli = {
    "debug_help": "Nivel de log DEBUG",
    "fps_gif_help": "Fotogramas por segundo del GIF animado.",
    "gif_help": "Genera un GIF animado a partir del vídeo indicado",
    "invalid_path": "{path} no es un archivo.",
    "output_help": "Nombre del archivo de salida.",
    "overwrite_confirm": "El archivo de salida ya existe. ¿Sobrescribir?",
    "overwrite_help": "Acción a usar si el archivo de salida ya existe.",
    "path_argument_help": "Vídeo a procesar.",
    "path_list_argument_help": "Lista de vídeos a procesar.",
    "resize_height_help": "Altura objetivo, en píxeles, para redimensionar el vídeo.",
    "resize_upscale_help": "Permite ampliar más allá de las dimensiones de origen.",
    "resize_width_help": "Anchura objetivo, en píxeles, para redimensionar el vídeo.",
    "show_help": "Muestra este mensaje y sale.",
    "timestamp_end_help": "Punto temporal en que termina la generación del GIF.",
    "timestamp_start_help": "Punto temporal en que comienza la generación del GIF.",
}


# La validación de `config.toml` devuelve todos los errores en un mensaje,
# cada entrada se inicializa con un salto de línea para mayor claridad.
ConfigValidation = {
    "invalid_audio_bit_rate": "\nAjuste de configuración no válido: se espera que encode.audio_bit_rate sea uno de: {expected}.",
    "invalid_audio_codec": "\nAjuste de configuración no válido: se espera que encode.audio_codec sea uno de: {expected}.",
    "invalid_channels": "\nAjuste de configuración no válido: se espera que conflictive_concat.channels sea uno de: {expected}.",
    "invalid_default_container": "\nAjuste de configuración no válido: se espera que encode.default_container sea uno de: {expected}.",
    "invalid_fps": "\nAjuste de configuración no válido: se espera que conflictive_concat.fps sea uno de: {expected}.",
    "invalid_language": "\nAjuste de configuración no válido: se espera que app.language sea uno de: {expected}.",
    "invalid_stall_timeout": "\nAjuste de configuración no válido: se espera que app.stall_timeout sea un entero entre 30 y 600.",
    "invalid_video_codec": "\nAjuste de configuración no válido: se espera que encode.video_codec sea uno de: {expected}.",
    "invalid_video_crf": "\nAjuste de configuración no válido: se espera que encode.video_crf esté entre {min} y {max}.",
    "invalid_video_preset": "\nAjuste de configuración no válido: se espera que encode.video_preset sea uno de: {expected}.",
}


Debug = {
    "ffmpeg_command": "Comando FFmpeg: {cmd}",
    "ffprobe_data": "Datos de ffprobe: {data}",
}


ExecutionError = {
    "cannot_create_directory": "No se pudo crear el directorio: {path}",
    "command_execution": "El comando FFmpeg {command_name} falló durante la ejecución. Error: {error}",
    "command_generation": "El comando FFmpeg {command_name} no se generó.",
    "command_timeout": "El comando FFmpeg {command_name} agotó el tiempo de espera.",
    "invalid_config": "Configuración no válida: {message}",
}


Info = {
    "gif_success": "GIF generado correctamente: {output}",
}


ParameterError = {
    "conflictive_output_parameters": "No se permite especificar una ruta de salida y un directorio de salida a la vez.",
    "conflictive_resize_dimensions_parameters": "No se permite especificar anchura y altura a la vez.",
    "missing_argument": "Falta el argumento: {argument}",
    "missing_media": "Falta información de vídeo: {path}",
    "missing_media_property": "Falta la propiedad del vídeo: {name}",
    "missing_parameter": "Falta el parámetro: {name}",
    "output_parameter": "No se permite especificar una salida si se han proporcionado varias entradas de vídeo.",
}


Progress = {
    "gif": "Generando GIF",
}


ValidationError = {
    "crop_exceeds_dimensions": "Dimensiones de recorte no válidas: {crop_dimensions} >= original {video_dimensions}.",
    "invalid_borders_format": "Formato de bordes no válido. Esperado: IZQUIERDA,DERECHA,SUPERIOR,INFERIOR.",
    "invalid_crop_format": "Formato de recorte no válido. Esperado: ANCHO,ALTO,X,Y.",
    "invalid_directory_name": '{directory} contiene caracteres no válidos: < > : " / \\ | ? *',
    "invalid_extension": "Extensión {extension} no válida. El códec {codec} requiere una de: {supported}.",
    "invalid_filename": '{filename} contiene caracteres no válidos: < > : " / \\ | ? *',
    "invalid_container_type": "Extensión {extension} no válida. {media_type} requiere una de: {supported}.",
    "invalid_time_format": "Formato de marca de tiempo no válido. Esperado: hh:mm:ss.",
    "time_exceeds_duration": "La marca de tiempo {time} supera la duración del vídeo {duration}.",
}


Warnings = {
    "overwrite_skipped": "Comando omitido porque el archivo de salida ya existe.",
    "resize_rejected_equal": "Redimensionado rechazado porque {dimension} es igual.",
    "upscale_rejected": "Redimensionado rechazado porque no_upscale es True y el objetivo {target} es mayor que el origen {source}.",
}
