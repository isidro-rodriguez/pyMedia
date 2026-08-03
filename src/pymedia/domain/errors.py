class PipelineValidationError(ValueError):
    """Error base de validación del pipeline."""


class NoVideoStreamError(PipelineValidationError):
    """El archivo no tiene stream de vídeo."""


class InvalidCropFormatError(PipelineValidationError):
    """Formato de crop inválido."""


class CropExceedsResolutionError(PipelineValidationError):
    """Valores de corte exceden la resolución."""


class InvalidScaleError(PipelineValidationError):
    """Valor de escala inválido."""
