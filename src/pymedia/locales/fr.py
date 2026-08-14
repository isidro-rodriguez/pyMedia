# ruff: noqa

Cli = {
    "concat_help": "Concatène les vidéos dans l'ordre spécifié",
    "crop_help": "Recadre selon le nombre de pixels spécifié. [dim]Ex. : -c 200,200,0,0[/dim]",
    "debug_help": "Niveau de journalisation DEBUG",
    "encode_help": "Transcode selon les options sélectionnées (au moins une option requise)",
    "end_point_help": "Point temporel auquel la génération du GIF se termine. [dim]Ex. : -ep 1:20[/dim]",
    "fps_help": "Nombre d'images par seconde du GIF animé. [dim]Ex. : -f 12[/dim]",
    "gif_help": "Génère un GIF animé à partir de la vidéo spécifiée",
    "gyrate_help": "Fait pivoter le média selon l'angle spécifié en degrés. [dim]Ex. : -g 90[/dim]",
    "invalid_path": "{path} n'est pas un fichier.",
    "output_help": "Nom du fichier de sortie. [dim]Ex. : -o cut.mp4[/dim]",
    "output_on_conflict_help": "Action à effectuer si un fichier portant le même nom existe déjà. [dim]Ex. : -oc rename[/dim]",
    "path_argument_help": "Vidéo à traiter.",
    "paths_argument_help": "Liste des vidéos à traiter.",
    "remux_help": "Réencode selon le profil spécifié dans la configuration.",
    "scale_gif_help": "Redimensionne proportionnellement le média à la hauteur spécifiée. [dim]Ex. : -s 240[/dim]",
    "scale_video_help": "Redimensionne proportionnellement le média à la hauteur spécifiée. [dim]Ex. : -s 240[/dim]",
    "show_help": "Affiche ce message et quitte.",
    "split_help": "Découpe une vidéo aux points spécifiés",
    "start_point_help": "Point temporel auquel la génération du GIF commence. [dim]Ex. : -sp 1:20[/dim]",
    "trim_points_help": "Points de découpe de la vidéo. [dim]Ex. : -t 00:10,00:20,00:30[/dim]",
}


ConfigValidation = {
    "invalid_audio_bit_rate": "\nParamètre de configuration invalide : encode.audio_bit_rate doit être l'une des valeurs suivantes : {expected}",
    "invalid_audio_codec": "\nParamètre de configuration invalide : encode.audio_codec doit être l'un des codecs suivants : {expected}",
    "invalid_channels": "\nParamètre de configuration invalide : conflictive_join.channels doit être l'une des valeurs suivantes : {expected}",
    "invalid_default_container": "\nParamètre de configuration invalide : encode.default_container doit être l'un des conteneurs suivants : {expected}",
    "invalid_fps": "\nParamètre de configuration invalide : conflictive_join.fps doit être l'une des valeurs suivantes : {expected}",
    "invalid_language": "\nParamètre de configuration invalide : app.language doit être l'une des valeurs suivantes : {expected}",
    "invalid_resize_to": "\nParamètre de configuration invalide : conflictive_join.resize_to doit être l'une des valeurs suivantes : {expected}",
    "invalid_video_codec": "\nParamètre de configuration invalide : encode.video_codec doit être l'un des codecs suivants : {expected}",
    "invalid_video_crf": "\nParamètre de configuration invalide : encode.video_crf doit être compris entre {min} et {max}",
    "invalid_video_preset": "\nParamètre de configuration invalide : encode.video_preset doit être l'un des profils suivants : {expected}",
}


Debug = {
    "ffmpeg_command": "Commande FFmpeg : {cmd}",
    "ffprobe_data": "Données ffprobe : {data}",
    "pipeline_crop": "Recadrage calculé : {crop}",
    "pipeline_gyrate": "Rotation appliquée : {gyrate}",
    "pipeline_scale": "Mise à l'échelle calculée : {scale}",
    "pipeline_time": "Temps traité : {time}",
    "pipeline_trim": "Points de découpe : {trim}",
}


ExecutionError = {
    "cannot_create_directory": "Impossible de créer le répertoire : {path}",
    "command_execution": "La commande FFmpeg '{command_name}' a échoué lors de son exécution. Erreur : {error}",
    "command_generation": "La commande FFmpeg '{command_name}' n'a pas été générée.",
    "ffmpeg_timeout": "L'opération FFmpeg a dépassé le délai d'attente autorisé.",
    "invalid_config": "Configuration invalide : {message}",
    "invalid_config_setting": "Paramètre de configuration invalide : {setting} doit être {expected}",
    "missing_config_section": "Section de configuration manquante : {section}",
    "missing_config_setting": "Paramètre de configuration manquant : {setting}",
    "unexpected_config_setting": "Paramètre de configuration inattendu : {setting}",
}


Info = {
    "config_saved": "Enregistrement de config.toml",
    "concat_success": "Vidéos concaténées avec succès : {output}",
    "encode_success": "Transcodage terminé avec succès : {output}",
    "gif_success": "GIF généré avec succès : {output}",
    "split_success": "Vidéo découpée avec succès : {output}",
}


PipelineError = {
    "incompatible_files": "Les fichiers vidéo sont incompatibles entre eux.",
    "missing_arguments": "Arguments manquants récupérés depuis Typer.",
    "missing_argument": "Argument manquant : {argument}",
    "missing_media": "Les informations du média '{path}' sont introuvables.",
    "missing_media_property": "La propriété du média '{property_name}' est introuvable.",
    "output_on_conflict": "Processus interrompu car le fichier de sortie existe déjà.",
}


Progress = {
    "concat": "Concaténation",
    "encode": "Transcodage",
    "gif": "Génération du GIF",
    "split": "Découpage",
}


ValidationError = {
    "crop_all_zero": "Recadrage invalide : toutes les valeurs sont égales à 0.",
    "crop_exceeds_height": "Recadrage invalide : {total} >= hauteur d'origine {height}.",
    "crop_exceeds_width": "Recadrage invalide : {total} >= largeur d'origine {width}.",
    "insufficient_inputs": "Au moins deux vidéos doivent être fournies pour cette commande.",
    "invalid_crop_format": "Format de recadrage invalide. Format attendu : LEFT,RIGHT,TOP,BOTTOM",
    "invalid_directory_name": "'{directory}' contient des caractères invalides : '< > : \" / \\ | ? *'",
    "invalid_extension": "Extension '{extension}' invalide. Le codec '{codec}' nécessite l'une des extensions suivantes : {supported}",
    "invalid_filename": "'{filename}' contient des caractères invalides : '< > : \" / \\ | ? *'",
    "invalid_gyrate": "Format de rotation invalide. Valeur attendue : 90 | 180 | 270.",
    "invalid_time_format": "Format d'horodatage invalide. Format attendu : hh:mm:ss.",
    "invalid_trim_points": "Points de découpe invalides.",
    "missing_options": "Au moins une option est requise.",
    "negative_time": "L'horodatage ne peut pas être négatif.",
    "time_exceeds_duration": "L'horodatage {time} dépasse la durée de la vidéo {duration}.",
}


Warnings = {
    "missing_options": "Au moins une option est requise.",
    "output_exist": "Le fichier existe déjà : {file_path}",
    "scale_rejected_equal": "Mise à l'échelle refusée : {scale} = hauteur d'origine {height}.",
    "scale_rejected_increase": "Mise à l'échelle à {scale}p non appliquée : la résolution est supérieure à celle d'origine ({height}p).",
}
