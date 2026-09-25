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

## Tasking

- Usar directorio `.kilo/temp/` para temporales de tarea como scripts, tests, etc. 
  **Limpiar el directorio al finalizar la implementación de la tarea**. Si existiesen ficheros 
  previos a la tarea, borrarlos.
- Si estás en modo PLAN, solo planificar la tarea; bajo ninguna circunstancia modificar 
  ficheros del repositorio ni crear ramas/worktrees.
- Al pasar a ACT (ejecución):
  1. Crear/preparar el worktree en `.kilo/worktrees/agent` sobre una rama `agent` basada en `main`.
  2. Realizar todo el desarrollo y validaciones (`uv run pytest`, linters) dentro del worktree.
  3. Al completar los cambios, presentar el resumen y solicitar aprobación explícita al  
     desarrollador.
  4. Una vez aprobada: integrar los cambios en `main` (fast-forward o merge según se indique), 
     eliminar el worktree temporal y limpiar `.kilo/temp/`.


## Tooling

- `uv` para paquetes
- `ruff` para lint/format
- `ty` para el tipado
- `pytest` para testeo

## Pre-commit checklist (orden estricto, detener en el primer fallo)

```bash
uv run ruff format
uv run ruff check --fix
uv run ruff check
uv run pytest
uv run pytest -m locales
# Si se ha tocado mensajes:
uv run python scripts/i18n.py extract
uv run python scripts/i18n.py update -l es
uv run python scripts/i18n.py compile -l es
uv run python scripts/i18n.py check
uv run pytest -m locales
```
