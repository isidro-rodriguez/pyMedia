import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import platformdirs


@dataclass(frozen=True)
class Transcode:
    video_codec: str
    video_preset: str
    video_crf: int
    video_pix_fmt: str
    audio_codec: str
    audio_bit_rate: str


@dataclass(frozen=True)
class ConflictiveJoin:
    resize_to: str
    fps: str
    channels: str
    pix_fmt: str
    confirm_transcode: bool


@dataclass(frozen=True)
class Config:
    transcode: Transcode
    conflictive_join: ConflictiveJoin

    @classmethod
    def load(cls) -> "Config":
        path = (
            Path(platformdirs.user_config_dir("pymedia", appauthor=False, roaming=True))
            / "config.toml"
        )
        if not path.exists():
            cls._create(path)

        with path.open("rb") as f:
            data = tomllib.load(f)
            cls._validate(data)

        return cls(
            transcode=Transcode(**data["transcode"]),
            conflictive_join=ConflictiveJoin(**data["conflictive_join"]),
        )

    @classmethod
    def save(cls) -> None:
        print("Guardando config.toml")
        # TODO: implementar posible manipulación de config.toml desde app

    @classmethod
    def _create(cls, path: Path) -> None:
        """Copia el config por defecto desde los recursos a la ruta de usuario."""
        print("Guardando config.toml")
        path.parent.mkdir(parents=True, exist_ok=True)
        src = (
            files("pymedia.resources")
            .joinpath("config.toml")
            .read_text(encoding="utf-8")
        )
        path.write_text(src, encoding="utf-8")

    @classmethod
    def _validate(cls, data: dict) -> None:
        print("")
        # TODO: implementar validación de config.toml
