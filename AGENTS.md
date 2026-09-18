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
1. `ruff check --fix`
2. `ruff format`
3. `ruff check`
4. `mypy --strict`
5. `pytest`
6. Comprobar VERSION, parar si se han añadido características sin aumentar versión
7. Si VERSION incrementada, actualizar CHANGELOG y README