from pymedia.models.enums import CropMargins, GyrateMode


def crop_to_cmd(crop: CropMargins) -> str:
    """Retorna el string para el filtro de crop."""
    return f"crop={crop.width}:{crop.height}:{crop.x}:{crop.y}"


def gyrate_to_cmd(gyrate: GyrateMode) -> str:
    """Retorna el string para el filtro de giro."""
    return {
        gyrate.d90: "transpose=1",
        gyrate.d180: "vflip,hflip",
        gyrate.d270: "transpose=2",
    }[gyrate]


def scale_to_cmd(scale: int) -> str:
    """Retorna el string para el filtro de scale."""
    return f"scale=-2:{scale}"
