"""Pipeline base para los pipelines de comandos."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

from pymedia.data.types import OverwriteMode


@dataclass(frozen=True, kw_only=True, slots=True)
class BaseArguments:
    """Base para los dataclasses de argumentos de comandos.

    Attributes:
        output: Ruta absoluta del fichero de salida.
        overwrite: Política ante conflicto de salida ya existente.
    """

    output: Path | None
    overwrite: OverwriteMode


@dataclass(kw_only=True)
class BaseParameters(ABC):
    """Base para los dataclasses de parámetros de comandos.

    Attributes:
        overwrite: Política ante conflicto de salida ya existente.
    """

    overwrite: OverwriteMode

    @abstractmethod
    def create(self) -> "BaseParameters":
        """Método abstracto para forzar a que los dataclasses hijos lo utilicen."""
        pass
