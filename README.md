# Python Boilerplate

Boilerplate moderno y minimalista para proyectos en Python (3.12+), optimizado para `uv`, `ruff` y `pytest`.

---

## 🚀 Instalación y Configuración

```bash
# Crear el entorno virtual e instalar todas las dependencias (desarrollo y producción)
uv sync

# Crear manualmente solo el entorno virtual
uv venv
```

---

## 🛠️ Comandos Habituales

```bash
# Ejecutar el script principal (definido en pyproject.toml -> [project.scripts])
uv run main

# Ejecutar la suite de pruebas unitarias
uv run pytest

# Analizar errores de código, imports y buenas prácticas (Linter)
uv run ruff check

# Corregir automáticamente errores de linting que sean solucionables
uv run ruff check --fix

# Formatear el código automáticamente según el estándar PEP 8
uv run ruff format

# Añadir una dependencia de producción (ej: pydantic, requests)
uv add pydantic

# Añadir una dependencia solo para desarrollo (ej: pytest-cov)
uv add --dev pytest-cov

# Eliminar una dependencia existente
uv remove pydantic

# Sincronizar y actualizar el archivo de bloqueo (uv.lock)
uv lock
```

---

## 📁 Estructura del Proyecto

```bash
.
├── src/
│   └── python_boilerplate/
│       ├── __init__.py
│       └── main.py          # Lógica del punto de entrada
├── tests/
│   └── test_main.py         # Pruebas unitarias con pytest
├── AGENTS.md                # Reglas de conducta y guía para agentes IA
├── pyproject.toml           # Configuración del proyecto, scripts, ruff y pytest
└── README.md                # Guía de uso y comandos del proyecto
```
