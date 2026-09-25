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

El agente trabaja en **espacio aislado** (worktree), de forma que cualquier error, experimento o 
fallo del agente no afecte al árbol principal (`main`). El worktree es **desechable**: si el agente 
muere o se cancela la tarea, se elimina sin consecuencias en `main`.

### PLAN (planificación)

- Solo leer. Bajo ninguna circunstancia modificar ficheros del repositorio, ni crear ramas, ni crear
  worktrees, ni escribir fuera de `.kilo/temp/`.
- Si la tarea es clara, pasar directamente a ACT.

### ACT (ejecución)

1. Preparar el worktree en `.kilo/worktrees/<task-id>` sobre una rama `<task-id>`
   recreada desde `main` (`git checkout -B <task-id> main`).
   - El worktree es una copia de trabajo de `main`; todos los cambios del agente se hacen aquí.
   - `.kilo/temp/` es para scripts, tests y artefactos temporales de la tarea. Limpiarlo al final.
2. **Desarrollo y validación**, pre-commit, dentro del worktree:
   - `uv run ruff format`
   - `uv run ruff check --fix`
   - `uv run ruff check`
   - `uv run ty check`
   - `uv run pytest`
   - `uv run pytest -m locales`
   - Si se han tocado mensajes de i18n:
     - `uv run python scripts/i18n.py extract`
     - `uv run python scripts/i18n.py update -l es`
     - `uv run python scripts/i18n.py compile -l es`
     - `uv run python scripts/i18n.py check`
     - `uv run pytest -m locales`
3. **Al completar**, redactar en informe diff en `.kilo/plans/<task-id>_diff` y presentar un 
   resumen de 
   los cambios y **solicitar aprobación explícita** al desarrollador. No integrar en `main` sin
   aprobación.
4. **Una vez aprobada** la tarea:
   - Integrar los cambios en `main` (fast-forward o merge según se indique).
   - Eliminar el worktree temporal.
   - Eliminar la rama `<task-id>` (`git branch -D <task-id>`)
   - Limpiar `.kilo/temp/` (si existían ficheros previos a la tarea, borrarlos).

### Seguridad del worktree

- Si el agente falla o se cancela, `main` queda intacto; el worktree se puede eliminar sin más.
- Los comandos de integración (`merge` / `fast-forward`) se ejecutan desde el repositorio principal,
  no desde el worktree.
