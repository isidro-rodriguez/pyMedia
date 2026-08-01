# Python Cheatsheet

## Variables y tipos

```python
nombre: str = "Ana"
edad: int = 30
precio: float = 9.99
es_activo: bool = True
nulo: None = None
```

## Control de flujo

```python
if edad >= 18:
    print("Adulto")
elif edad >= 13:
    print("Adolescente")
else:
    print("Niño")

for i in range(5):  # 0..4
    print(i)

while edad > 0:
    edad -= 1
```

## Funciones

```python
def saludar(nombre: str, saludo: str = "Hola") -> str:
    return f"{saludo}, {nombre}"


print(saludar("Mundo"))
```

## Estructuras de datos

```python
lista = [1, 2, 3]
lista.append(4)
lista[0]  # 1
lista[-1]  # 4

diccionario = {"clave": "valor"}
diccionario["clave"]  # "valor"
diccionario.get("otra", "default")

conjunto = {1, 2, 3}
conjunto.add(4)

tupla = (1, 2, 3)
a, b, c = tupla  # unpacking
```

## Comprehensions

```python
cuadrados = [x**2 for x in range(10)]
pares = [x for x in range(20) if x % 2 == 0]
cuadrados_dict = {x: x**2 for x in range(5)}
```

## Manejo de errores

```python
try:
    resultado = 10 / 0
except ZeroDivisionError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
else:
    print("Todo bien")
finally:
    print("Limpieza")
```

## Archivos

```python
with open("archivo.txt", "r", encoding="utf-8") as f:
    contenido = f.read()

with open("salida.txt", "w", encoding="utf-8") as f:
    f.write("Hola mundo")
```

## Módulos

```python
# Importar módulo
import math

# Importar con alias
import numpy as np

# Importar específico
from pathlib import Path

# Ejecutar como script
if __name__ == "__main__":
    main()
```

## F-strings

```python
nombre = "Ana"
edad = 30
mensaje = f"{nombre} tiene {edad} años"
ancho = 10
alineado = f"{nombre:>{ancho}}"  # "      Ana"
```

## Decoradores

```python
def mi_decorador(func):
    def wrapper(*args, **kwargs):
        print("Antes")
        resultado = func(*args, **kwargs)
        print("Después")
        return resultado

    return wrapper


@mi_decorador
def saludar():
    print("Hola")
```

## Generadores

```python
def generador_pares(n):
    for i in range(n):
        if i % 2 == 0:
            yield i


for par in generador_pares(10):
    print(par)
```

## Match / Case (Python 3.10+)

```python
def responder(comando):
    match comando:
        case "hola":
            return "¡Hola!"
        case "adios":
            return "¡Chao!"
        case _:
            return "No entiendo"
```

## Type hints básicos

```python
from typing import List, Optional


def procesar(nombres: List[str], limite: Optional[int] = None) -> List[str]:
    resultado = [n.upper() for n in nombres]
    if limite:
        resultado = resultado[:limite]
    return resultado
```

## Pathlib (recomendado sobre os.path)

```python
from pathlib import Path

ruta = Path("src") / "mi_modulo" / "main.py"
print(ruta.exists())
print(ruta.read_text(encoding="utf-8"))
```

## Operadores útiles

```python
# Walrus operator (Python 3.8+)
if (n := len(lista)) > 10:
    print(f"Lista larga: {n} elementos")

# Unpacking extendido
a, *resto, ultimo = [1, 2, 3, 4, 5]

# Swap sin temporal
a, b = b, a

# Merge de diccionarios
d1 = {"a": 1}
d2 = {"b": 2}
fusionado = {**d1, **d2}
```

## Builtins frecuentes

```python
abs(-5)  # 5
all([True, True])  # True
any([False, True])  # True
enumerate(lista)  # (0, 'a'), (1, 'b')...
len(lista)  # longitud
max(lista)  # máximo
min(lista)  # mínimo
sorted(lista)  # nueva lista ordenada
sum(lista)  # suma
zip(lista1, lista2)  # (a1, b1), (a2, b2)...
```
