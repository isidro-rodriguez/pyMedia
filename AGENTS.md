# Agent Guidelines — Python

Código simple, legible, stdlib antes que dependencias nuevas.

## Style (PEP8 + Ruff)

- Orden imports: stdlib > third-party > local
- Sin mutable default args
- Funciones: responsabilidad única, ~20 líneas máximo
- Nunca silenciar errores

## Types & Docs

- Type hints estrictos (MyPy)
- Docstrings Google-style: completos en público, una línea en privado/anidado
- Docstring público hereda `Raises` de las funciones privadas que llama
- Comentarios explican el *porqué*, no el *qué*.

## Ahorro de tokens

- Previene bucles: no reintentes comandos fallidos más de 2 veces.
- Ahorra contexto con respuestas concisas.
- Cambios eficientes, prioriza manipulaciones en masa.

## Testing

- pytest, Arrange-Act-Assert
- Testear parsers/calculadoras/edge cases, UI no
- Crear directorio `temp/` para scripts, tests o ficheros temporales. BORRARLO AL FINALIZAR.

## Tooling

- `uv` para paquetes
- `ruff` para lint/format
- `pytest` para testeo
- `mypy` para tipado

## Pre-commit checklist (orden estricto, detener en el primer fallo)

```bash
uv run ruff format
uv run ruff check --fix
uv run ruff check
uv run mypy --strict
uv run pytest
uv run pytest -m locales
# Si se ha tocado mensajes:
uv run python scripts/i18n.py extract
uv run python scripts/i18n.py update -l es
uv run python scripts/i18n.py compile -l es
uv run python scripts/i18n.py check
# Test de compilación
uv run pytest -q -m prod
# Comprobar versión: 
# - Parar si se han añadido características sin incrementar versión
# - Si se ha incrementado versión, actualizar CHANGELOG.md y README.md
```
