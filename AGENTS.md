# Guía de agente Python

Código simple, legible, stdlib antes que dependencias nuevas.

## Style (PEP8 + Ruff)

- Orden imports: stdlib > third-party > local.
- Sin mutable default args.
- Funciones: responsabilidad única, ~20 líneas máximo.
- Nunca silenciar errores.

## Types & Docs

- Type hints estrictos (Ty).
- Docstrings Google-style: completos en público, una línea en privado/anidado.
- Docstring público hereda `Raises` de las funciones privadas que llama.
- Comentarios explican el *porqué*, no el *qué*.

## Ahorro de tokens

- Previene bucles: no reintentes comandos fallidos más de 2 veces.
- Ahorra contexto con respuestas concisas.
- Cambios eficientes, prioriza manipulaciones en masa.

## Tooling

- `uv` para paquetes
- `ruff` para lint/format
- `ty` para el tipado
- `pytest` para testeo

## Tasking

General:

- Usar `.kilo/temp/` para alojar ficheros temporales de tarea (scripts, tests, ...).

En modo `PLAN`:

- Solo leer, **NO MODIFICAR** ficheros del repositorio fuera de `.kilo/temp/`.
- Presenta informe de planificación y esperar por confirmación.

En modo `ACT`:

1. Implementar la planificación confirmada.
2. Validar la implementación:
   - `uv run ruff format`
   - `uv run ruff check --fix`
   - `uv run ruff check`
   - `uv run ty check`
   - `uv run pytest`
   - `uv run pytest -m locales`
   - Si `pytest -m locales` falla:
     - `uv run python scripts/i18n.py extract`
     - `uv run python scripts/i18n.py update -l es`
     - `uv run python scripts/i18n.py compile -l es`
     - `uv run python scripts/i18n.py check`
     - `uv run pytest -m locales`
3. **Al completar**, presentar un resumen de cambios y limpiar `.kilo/temp/`.
