# Pythonic Code

Guía de código idiomático en Python. Lo que diferencia un código que "funciona" de uno que es legible, mantenible y expresivo.

## Principios generales

- **Legible explícitamente:** El código se lee como se habla.
- **Simple es mejor que complejo:** Prefiere soluciones claras antes que astutas.
- **No te repitas (DRY):** Si lo repites dos veces, abstraelo.
- **Errores explícitos:** Maneja lo que puede fallar, no catches silenciosos.

---

## Nombres

```python
# Bien: descriptivo y en minúsculas con guiones
def calcular_precio_total(productos: list[dict]) -> float: ...


# Mal: abreviaturas sin contexto
def calc_pp(ps): ...
```

## F-strings en vez de concatenación

```python
# Bien
mensaje = f"Usuario {usuario} tiene {intentos} intentos"

# Mal
mensaje = "Usuario " + usuario + " tiene " + str(intentos) + " intentos"
```

## Context managers con `with`

```python
# Bien: cierre automático
with open("archivo.txt") as f:
    datos = f.read()

# Mal: tienes que recordar cerrar
f = open("archivo.txt")
datos = f.read()
f.close()
```

## Iterar con enumerate, no con range(len)

```python
nombres = ["Ana", "Beto", "Carla"]

# Bien
for i, nombre in enumerate(nombres):
    print(f"{i}: {nombre}")

# Mal
for i in range(len(nombres)):
    print(f"{i}: {nombres[i]}")
```

## Iterar en paralelo con zip

```python
nombres = ["Ana", "Beto"]
edades = [25, 30]

# Bien
for nombre, edad in zip(nombres, edades):
    print(f"{nombre}: {edad}")

# Mal
for i in range(len(nombres)):
    print(f"{nombres[i]}: {edades[i]}")
```

## Comparar con `is None`, no `== None`

```python
if valor is None:
    manejar_nulo()
```

## Diccionarios: get() con default

```python
config = {"timeout": 5}
timeout = config.get("timeout", 10)  # 5
host = config.get("host", "localhost")  # "localhost"
```

## Return temprano (guard clauses)

```python
# Bien: casos borde primero
def procesar(pedido):
    if not pedido:
        return []
    if pedido["cantidad"] <= 0:
        return []
    return calcular(pedido)


# Mal: anidación profunda
def procesar(pedido):
    if pedido:
        if pedido["cantidad"] > 0:
            return calcular(pedido)
    return []
```

## List comprehensiones vs map/filter

```python
# Bien: comprehension
cuadrados = [x**2 for x in range(10)]
pares = [x for x in range(20) if x % 2 == 0]

# Solo usar map/filter cuando la lógica es compleja
```

## Evitar argumentos mutables por defecto

```python
# Bien
def agregar(item: str, lista: list[str] | None = None) -> list[str]:
    if lista is None:
        lista = []
    lista.append(item)
    return lista


# Mal: la lista se comparte entre llamadas
def agregar(item: str, lista=[]):
    lista.append(item)
    return lista
```

## Unpacking para asignaciones

```python
# Desempaquetar tupla
x, y, z = punto

# Swap sin temporal
a, b = b, a

# Capturar resto
primero, *resto, ultimo = [1, 2, 3, 4, 5]

# Merge de diccionarios
config = {**defaults, **usuario}
```

## Walrus operator para evitar repetición

```python
# Bien: calcula una vez, asigna y usa
if (n := len(datos)) > 100:
    print(f"Procesando {n} registros")

# Mal: calcula dos veces
n = len(datos)
if n > 100:
    print(f"Procesando {n} registros")
```

## Usar pathlib en vez de os.path

```python
from pathlib import Path

ruta = Path("src") / "modulo" / "main.py"

if ruta.exists():
    print(ruta.read_text(encoding="utf-8"))
```

## Excepciones específicas

```python
# Bien
try:
    resultado = 10 / int(entrada)
except ValueError:
    print("Entrada no numérica")
except ZeroDivisionError:
    print("División por cero")

# Mal: catch general
try:
    resultado = 10 / int(entrada)
except:
    pass
```

## Dataclasses para datos estructurados

```python
from dataclasses import dataclass
from datetime import date


@dataclass
class Usuario:
    nombre: str
    email: str
    activo: bool = True
    creado: date = date.today()


usuario = Usuario(nombre="Ana", email="ana@example.com")
```

## Type hints siempre que sea posible

```python
from typing import Optional


def buscar(nombre: str, edad: Optional[int] = None) -> dict:
    return {"nombre": nombre, "edad": edad}
```

## Evitar variables de una letra (excepto contadores)

```python
# Mal
x = 10
y = 20
z = x + y

# Bien
ancho = 10
alto = 20
area = ancho + alto
```

## Constantes en mayúsculas

```python
TIMEOUT_SEGUNDOS = 30
MAX_REINTENTOS = 3
MENSAJE_BIENVENIDA = "Bienvenido al sistema"
```

## No abuses de listas auxiliares

```python
# Bien: comprehension directo
nombres_mayusculas = [n.upper() for n in nombres]

# Mal: lista vacía y append
nombres_mayusculas = []
for n in nombres:
    nombres_mayusculas.append(n.upper())
```

## Docstrings en módulos, clases y funciones públicas

```python
def calcular_descuento(precio: float, porcentaje: float) -> float:
    """Calcula el descuento aplicado a un precio.

    Args:
        precio: Precio original del producto.
        porcentaje: Porcentaje de descuento (0-100).

    Returns:
        Precio final después del descuento.
    """
    return precio * (1 - porcentaje / 100)
```

## Resumen rápido

- Usa f-strings, no concatenación.
- Usa `with` para archivos y recursos.
- Usa `enumerate` y `zip` en bucles.
- Usa `pathlib` en vez de `os.path`.
- Pon type hints en funciones públicas.
- Usa dataclasses en vez de dicts anidados.
- Maneja excepciones específicas.
- Nombres descriptivos, no abreviaturas.
- Docstrings en lo público.
