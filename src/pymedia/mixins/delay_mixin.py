"""Mixin para desplazar en el tiempo una pista de audio o de subtítulos."""

from dataclasses import dataclass
from pathlib import Path

from pymedia.errors import UserError
from pymedia.locales import translate as _

MATROSKA_CONTAINERS = (".mkv", ".mka", ".webm")
"""Contenedores que admiten marcas de tiempo negativas al copiar subtítulos."""


@dataclass(kw_only=True)
class DelayMixin:
    """Desfase constante de una pista, sin recodificar.

    Attributes:
        delay: Segundos de desfase: positivo retrasa la pista, negativo la
            adelanta. `None` si no se desplaza.
    """

    delay: float | None = None

    def create_delay(
        self, delay: float | None, output: Path | None = None, subtitles: bool = False
    ) -> None:
        """Valida y guarda el desfase de la pista.

        Args:
            delay: Segundos de desfase indicados por el usuario.
            output: Fichero de salida, para validar el contenedor.
            subtitles: Si la pista desplazada es de subtítulos ya incluidos en
                el contenedor (se copian con sus marcas de tiempo).

        Raises:
            UserError: Si se adelantan subtítulos copiados a un contenedor que
                no es Matroska: MP4 descarta o deforma los eventos iniciales.
        """
        if not delay:
            self.delay = None
            return

        if (
            subtitles
            and delay < 0
            and output is not None
            and output.suffix not in MATROSKA_CONTAINERS
        ):
            raise UserError(
                msg=_(
                    "Subtitles can only be advanced (negative --delay) in a "
                    "Matroska output: %(containers)s."
                )
                % {"containers": ", ".join(MATROSKA_CONTAINERS)}
            )
        self.delay = delay

    def to_delay_input_cmd(self) -> list[str]:
        """Desfase de una entrada externa: va justo antes de su `-i`.

        Returns:
            `-itsoffset <segundos>`, o una lista vacía si no hay desfase.
        """
        if self.delay is None:
            return []
        return ["-itsoffset", _seconds(self.delay)]

    def to_delay_stream_cmd(self, stream: str) -> list[str]:
        """Desfase de una pista del contenedor copiada sin recodificar.

        El filtro de bitstream `setts` reescribe las marcas de tiempo de una sola
        pista, sin alterar el orden ni el resto de pistas del contenedor.

        Args:
            stream: Especificador de la pista de salida (`a:1`, `s:0`).

        Returns:
            `-bsf:<pista> setts=...`, o una lista vacía si no hay desfase.
        """
        if self.delay is None:
            return []
        sign = "+" if self.delay > 0 else "-"
        return [f"-bsf:{stream}", f"setts=ts=TS{sign}{_seconds(abs(self.delay))}/TB"]


def _seconds(value: float) -> str:
    """Segundos con precisión de milisegundo y sin ceros sobrantes."""
    return f"{value:.3f}".rstrip("0").rstrip(".")
