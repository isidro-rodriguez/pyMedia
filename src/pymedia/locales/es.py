# ruff: noqa

Cli = {
    'concat_help': 'Concatena los vídeos en el orden especificado',
    'crop_help': 'Recorta el número de píxeles especificado.',
    'debug_help': 'Nivel de registro DEBUG',
    'encode_help': 'Transcodifica usando las opciones seleccionadas (requiere al menos una opción)',
    'end_point_help': 'Punto temporal en el que finaliza la generación del GIF.',
    'fps_help': 'Fotogramas por segundo del GIF animado.',
    'gif_help': 'Genera un GIF animado a partir del vídeo especificado',
    'gyrate_help': 'Gira el medio el ángulo especificado en grados.',
    'invalid_path': '{path} no es un archivo.',
    'output_help': 'Nombre del archivo de salida.',
    'output_on_conflict_help': 'Acción que se realizará si ya existe un archivo con el mismo nombre.',
    'path_argument_help': 'Vídeo que se procesará.',
    'paths_argument_help': 'Lista de vídeos que se procesarán.',
    'remux_help': 'Reprocesa usando el perfil especificado en la configuración.',
    'scale_gif_help': 'Redimensiona el medio proporcionalmente a la altura especificada.',
    'scale_video_help': 'Redimensiona el medio proporcionalmente a la altura especificada.',
    'show_help': 'Muestra este mensaje y termina.',
    'split_help': 'Divide un vídeo en los puntos especificados',
    'start_point_help': 'Punto temporal en el que comienza la generación del GIF.',
    'trim_points_help': 'Puntos de división del vídeo.',
}

ConfigValidation = {
    'invalid_audio_bit_rate': '\nConfiguración no válida: encode.audio_bit_rate debe ser uno de: {expected}',
    'invalid_audio_codec': '\nConfiguración no válida: encode.audio_codec debe ser uno de: {expected}',
    'invalid_channels': '\nConfiguración no válida: conflictive_join.channels debe ser uno de: {expected}',
    'invalid_default_container': '\nConfiguración no válida: encode.default_container debe ser uno de: {expected}',
    'invalid_fps': '\nConfiguración no válida: conflictive_join.fps debe ser uno de: {expected}',
    'invalid_language': '\nConfiguración no válida: app.language debe ser uno de: {expected}',
    'invalid_resize_to': '\nConfiguración no válida: conflictive_join.resize_to debe ser uno de: {expected}',
    'invalid_video_codec': '\nConfiguración no válida: encode.video_codec debe ser uno de: {expected}',
    'invalid_video_crf': '\nConfiguración no válida: encode.video_crf debe estar entre {min} y {max}',
    'invalid_video_preset': '\nConfiguración no válida: encode.video_preset debe ser uno de: {expected}',
}

Debug = {
    'ffmpeg_command': 'Comando FFmpeg: {cmd}',
    'ffprobe_data': 'Datos de ffprobe: {data}',
    'pipeline_crop': 'Recorte calculado: {crop}',
    'pipeline_gyrate': 'Rotación aplicada: {gyrate}',
    'pipeline_scale': 'Escalado calculado: {scale}',
    'pipeline_time': 'Tiempo procesado: {time}',
    'pipeline_trim': 'Puntos de división: {trim}',
}

ExecutionError = {
    'cannot_create_directory': 'No se ha podido crear el directorio: {path}',
    'command_execution': "El comando de FFmpeg '{command_name}' ha fallado durante la ejecución. Error: {error}",
    'command_generation': "No se ha generado el comando de FFmpeg '{command_name}'.",
    'ffmpeg_timeout': 'La operación de FFmpeg ha superado el tiempo de espera permitido.',
    'invalid_config': 'Configuración no válida: {message}',
    'invalid_config_setting': 'Configuración no válida: {setting} debe ser {expected}',
    'missing_config_section': 'Falta la sección de configuración: {section}',
    'missing_config_setting': 'Falta el ajuste de configuración: {setting}',
    'unexpected_config_setting': 'Ajuste de configuración no esperado: {setting}',
}

Info = {
    'config_saved': 'Guardando config.toml',
    'concat_success': 'Vídeos concatenados correctamente: {output}',
    'encode_success': 'Transcodificación completada correctamente: {output}',
    'gif_success': 'GIF generado correctamente: {output}',
    'split_success': 'Vídeo dividido correctamente: {output}',
}

PipelineError = {
    'incompatible_files': 'Los archivos de vídeo no son compatibles entre sí.',
    'missing_arguments': 'Faltan argumentos obtenidos de Typer.',
    'missing_argument': 'Falta el argumento: {argument}',
    'missing_media': "No se ha podido encontrar información multimedia para '{path}'.",
    'missing_media_property': "No se ha podido encontrar la propiedad multimedia '{property_name}'.",
    'output_on_conflict': 'Proceso detenido porque el archivo de salida ya existe.',
}

Progress = {
    'concat': 'Concatenando',
    'encode': 'Transcodificando',
    'gif': 'Generando GIF',
    'split': 'Dividiendo',
}

ValidationError = {
    'crop_all_zero': 'Recorte no válido: todos los valores son 0.',
    'crop_exceeds_height': 'Recorte no válido: {total} >= altura original {height}.',
    'crop_exceeds_width': 'Recorte no válido: {total} >= anchura original {width}.',
    'insufficient_inputs': 'Se deben proporcionar al menos dos vídeos para este comando.',
    'invalid_crop_format': 'Formato de recorte no válido. Se espera: LEFT,RIGHT,TOP,BOTTOM.',
    'invalid_directory_name': '\'{directory}\' contiene caracteres no válidos: \'< > : " / \\ | ? *\'',
    'invalid_extension': "Extensión no válida '{extension}'. El códec '{codec}' requiere una de: {supported}.",
    'invalid_filename': '\'{filename}\' contiene caracteres no válidos: \'< > : " / \\ | ? *\'',
    'invalid_gif_extension': "Extensión no válida '{extension}'. Las imágenes GIF requieren el contenedor '.gif'.",
    'invalid_gyrate': 'Formato de rotación no válido. Se espera: 90 | 180 | 270.',
    'invalid_setting': 'Ajuste no válido: {parameter}',
    'invalid_time_format': 'Formato de marca de tiempo no válido. Se espera: hh:mm:ss.',
    'invalid_trim_points': 'Puntos de división no válidos.',
    'invalid_video_extension': "Extensión de vídeo no válida '{extension}'. Los archivos de vídeo requieren una de: {supported}.",
    'missing_options': 'Se requiere al menos una opción.',
    'negative_time': 'La marca de tiempo no puede ser negativa.',
    'time_exceeds_duration': 'La marca de tiempo {time} supera la duración del vídeo {duration}.',
}

Warnings = {
    'missing_options': 'Se requiere al menos una opción.',
    'output_exist': 'El archivo ya existe: {file_path}.',
    'scale_rejected_equal': 'Escalado rechazado: {scale} = altura original {height}.',
    'scale_rejected_increase': 'No se aplica el escalado a {scale}p: la resolución es superior a la original ({height}p).',
}
