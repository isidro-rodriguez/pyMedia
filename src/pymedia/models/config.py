import tomllib
from dataclasses import dataclass
from importlib.resources import files
from pathlib import Path

import platformdirs


@dataclass(frozen=True)
class Encode:
    video_codec: str
    video_preset: str
    video_crf: int
    audio_codec: str
    audio_bit_rate: str
    default_container: str


@dataclass(frozen=True)
class ConflictiveJoin:
    resize_to: str
    fps: str
    channels: str
    confirm_encode: bool


@dataclass(frozen=True)
class App:
    logger_level: str
    disable_resolution_increase: bool


@dataclass(frozen=True)
class Config:
    encode: Encode
    conflictive_join: ConflictiveJoin
    app: App

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
            encode=Encode(**data["encode"]),
            conflictive_join=ConflictiveJoin(**data["conflictive_join"]),
            app=App(**data["app"]),
        )

    @classmethod
    def _create(cls, path: Path) -> None:
        """Copia el config por defecto desde los recursos a la ruta de usuario."""
        path.parent.mkdir(parents=True, exist_ok=True)
        src = (
            files("pymedia.resources")
            .joinpath("config.toml")
            .read_text(encoding="utf-8")
        )
        path.write_text(src, encoding="utf-8")

    @classmethod
    def _validate(cls, data: dict) -> None:
        # TODO: implementar validación de config.toml
        pass
