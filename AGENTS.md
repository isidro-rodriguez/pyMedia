# Agent Guidelines — Python

Código simple, legible, stdlib antes que dependencias nuevas.

## Style (PEP8 + Ruff)
- Orden imports: stdlib > third-party > local
- Sin mutable default args
- Funciones: responsabilidad única, ~20 líneas máximo

## Types & Docs
- Type hints estrictos (MyPy)
- Docstrings Google-style: completos en público, una línea en privado/anidado
- Docstring público hereda `Raises` de las funciones privadas que llama
- Comentarios explican el *por qué*, no el *qué*; nada de código comentado, prints de debug, o contexto de prompt/tarea filtrado

## Errors
- Nunca silenciar errores — log o comentario mínimo

## Security
- Sin secretos hardcodeados — env vars / `.env` (gitignored)
- Nunca loggear tokens/passwords/PII

## Testing
- pytest, Arrange-Act-Assert
- Testear parsers/calculadoras/edge cases; UI no

## Tooling
- `uv` para paquetes
- Ruff para lint/format

## Pre-commit checklist (orden estricto, detener en el primer fallo)
1. `ruff check --fix`
2. `ruff format`
3. `ruff check`
4. `mypy --strict`
5. `pytest`
6. VERSION actualizada si aplica
7. CHANGELOG actualizado si aplica
8. README actualizado si aplica