from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    cosa_1: str
    cosa_2: str
    cosa_3: str


def config_loader() -> Config:
    return Config(
        cosa_1="valor_1",
        cosa_2="valor_2",
        cosa_3="valor_3",
    )
