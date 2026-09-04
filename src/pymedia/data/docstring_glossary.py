# ruff: noqa
"""Glosario de docstrings de pyMedia.

Documento de referencia interno. Contiene la definición canónica de cada
atributo, argumento y frase fija de los docstrings del proyecto, pensada
para copiar/pegar directamente.

Reglas de consistencia
----------------------
1. Un mismo atributo usa EXACTAMENTE la misma definición en todos los
   docstrings, carácter por carácter (mayúsculas, acentos y punto final
   incluidos).
2. Los dataclasses ``*Arguments`` (crudos de CLI) y ``*Parameters``
   (procesados) usan capas de glosario distintas: ``ARGUMENTS`` y
   ``PARAMETERS``. Nunca mezclarlas.
3. Excepción: los docstrings que hacen referencia al comando en el que están
   (p. ej. Imágenes por segundo del GIF.) pueden añadir ese matiz, pero
   manteniendo el formato ``<definición base> <matiz>``.
4. En caso de clave duplicada entre varios comandos o módulos, pero con
   distinta descripción repetida, se ubicará una marca #COMANDO o #MÓDULO
   (si no pertenece a un dataclass de pipeline), fuera de los 76 caracteres
   para aclarar a qué comando pertenece.
5. Los ``Returns:`` de los ``to_*_cmd`` siguen la plantilla:
   ``Filtro/lista/str... listo/lista para el consumo de ffmpeg.``
6. La combinación `key: descripción` <= 76 caracteres.


===========================================================================
 Atributos de dataclasses ARGUMENTS y PARAMETERS
===========================================================================
crop: Área y coordenada de la zona a preservar de la imagen.
crop_area: Área y coordenada, en px, de la zona a preservar de la imagen.
crop_borders: Cantidad de píxeles a recortar de cada borde.
every: Tiempo necesario, en segundos, para tomar cada captura.
fps: Imágenes por segundo del GIF.                                          # GIF
fps: Frecuencia de imágenes por segundo a extraer.                          # THUMBNAIL
hflip: Invierte la imagen horizontalmente, intercambia izquierda y derecha.
input_counter: Cantidad de ficheros a procesar.
input_list: Lista de rutas de los ficheros de vídeo a procesar.
input_single: Ruta del fichero de vídeo a procesar.
media: Metadatos del vídeo de entrada ya resuelto y validado.
media_list: Lista de metadatos de los vídeos a procesar.
output: Ruta absoluta del fichero de salida procesado.
output_directory: Directorio de salida para lotes de ficheros.
overwrite: Política ante conflicto de salida ya existente.
preset_sheet: Estilo de hoja preajustado.
rotate: Ángulo ortogonal con el que se va a rotar la imagen.
scale_mode: Política de escalado del vídeo o imagen.
scale_to: Dimensión objetivo en píxeles.
scale_upscale: Permite el incremento de dimensiones.
scene: Umbral de sensibilidad para detección de cambio de escena.
timestamp_at: Lista de marcas de tiempo.
timestamp_end: Marca de tiempo que indica el punto final.
timestamp_start: Marca de tiempo que indica el punto inicial.
vflip: Invierte la imagen verticalmente, intercambiando arriba y abajo.


===========================================================================
 Argumentos de métodos y funciones (usar los attr de dataclasses también)
===========================================================================
affix: Sufijo a añadir al nombre del fichero de salida.
app: Instancia de Typer en la que se registra el comando.
args: Argumentos tipados específicos del comando.
args_cls: Clase de argumentos cuya firma define los campos válidos.
cmd: Comando ffmpeg ya construido, listo para ejecutar.
command_name: Nombre del comando.
config: Parámetros que determinan el funcionamiento de la aplicación.
crop_str: String con el valor de crop indicado por el usuario.
debug: Habilita el nivel de log DEBUG.
description: Mensaje a mostrar junto a la barra de progreso.
timestamp_end: Marca de tiempo que indica el punto final.
extension: Extensión del fichero de salida.
fps: Frecuencia de imágenes por segundo.                                    # MEDIA
fps: Si transcodifica los vídeos al de menor FPS o el mayor.                # CONFIG
help_: Helper para mostrar esta línea en distintos idiomas.
local_vars: Variables locales de la función.
logger: Interfaz principal de la aplicación para generar mensajes.
media_type: Tipo de medio de salida esperado.
params: Parámetros parseados y validados a partir de `args`.
path: Ruta del fichero de vídeo a procesar.
path: Ruta del fichero cuyos metadatos no se obtuvieron.                    # ERRORS
progress_time: Duración del tramo de vídeo a procesar.
stall_timeout: Tiempo de espera por estancamiento.
timestamp_start: Marca de tiempo que indica el punto inicial.
time: Marca de tiempo con la que comparar.
time: Duración a formatear.                                                 # UTILS
times_str: String de lista de marcas de tiempo.
total_steps: Número de pasos esperados de `showinfo` por stderr.
video_duration: Duración del vídeo a procesar.


===========================================================================
 RAISES
===========================================================================
CommandError: Si falla el cmd o se bloquea.
CommandGenerationError: Si no se pudo construir el comando ffmpeg.
ConfigError: Si algún valor de configuración no es válido.
ExclusiveOptionsError: Si se indican opciones incompatibles entre sí.
InvalidArgumentError: Si el argumento no tiene un formato válido.
InvalidContainerError: Si el contenedor no corresponde al códec usado.
InvalidContainerTypeError: Si el contenedor no corresponde al tipo de medio.
InvalidParameterError: Si el parámetro no tiene un valor válido.
InvalidTimeFormatError: Si el formato de la marca de tiempo no es válido.
MissingMediaError: Si no se pudieron obtener los metadatos del fichero.
MissingMediaPropertyError: Si no se pudo obtener la propiedad del vídeo.
MissingParameterError: Si no se pudo obtener el parámetro.
MissingRequiredOptionError: Si faltaron opciones requeridas.
OptionError: Si valores de opciones que provocan acciones inesperadas.
PermissionDeniedError: Si el usuario no tiene permisos de escritura.
TimeExceedsDurationError: Si el tiempo supera la duración del vídeo.
"""
