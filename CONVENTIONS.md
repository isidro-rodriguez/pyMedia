# Conventions

Internal conventions for this project. Not a public API contract — just
consistency rules so the codebase stays predictable as it grows.

## Docstrings

Google style. Description starts on its own line after the opening
`"""`, not inline with them.

```python
def process_crop(crop: str, media: Media, dimensions: tuple[int, int]) -> list[int]:
    """
    Valida, parsea y procesa la opción de corte.

    Args:
        crop: Valor de las dimensiones de corte.
        media: Datos del vídeo a procesar.
        dimensions: Dimensiones normalizadas para CONCAT incompatible.

    Returns:
        Lista de las dimensiones de corte.

    Raises:
        CropExceedsDimensionsError: Si el corte excede el vídeo original.
        InvalidCropFormatError: Si el formato no es parseable.
    """
```

- **Public functions/classes**: full Google-style docstring.
- **Private (`_name`) or nested functions**: single-line comment/docstring
  is enough — the scope already limits who reads it.

## Function naming

| Prefix          | Returns          | Contract                                                        |
|------------------|-------------------|-------------------------------------------------------------------|
| `is_valid_*`, `has_*`, `can_*` | `bool`            | Pure predicate. No side effects, no raising.                     |
| `validate_*`     | `None`            | Guard. Raises a `PyMediaError` subclass if invalid, returns nothing otherwise. |
| `parse_*`        | `Tipo`            | Pure transform from raw/string input to a typed value. Only does that. |
| `to_*` / `as_*`   | `Tipo`            | Conversion between already-validated types.                      |
| `from_*`         | instance (usually `@classmethod`) | Alternative constructor.                          |
| `build_*` / `make_*` / `create_*` | object | Assembles a composite object from parts.                  |
| `process_*`      | `Tipo`            | Orchestrator: calls `validate_*` + `parse_*` (+ others) in sequence. |

Example of the intended composition:

```python
def is_valid_crop(crop: CropMargins, media: Media) -> bool:
    """Comprueba si el corte es compatible con las dimensiones del vídeo."""
    ...

def validate_crop(crop: CropMargins, media: Media) -> None:
    """Valida el corte y lanza si excede las dimensiones.

    Raises:
        CropExceedsDimensionsError: Si el corte excede el vídeo original.
    """
    if not is_valid_crop(crop, media):
        raise CropExceedsDimensionsError(...)

def parse_crop(raw: str) -> CropMargins:
    """Parsea el string de --crop a CropMargins."""
    ...

def process_crop(raw: str, media: Media) -> CropMargins:
    """Valida y parsea la opción de corte de principio a fin."""
    crop = parse_crop(raw)
    validate_crop(crop, media)
    return crop
```

## Nested functions

Use nested functions to keep one-off internal logic close to where it's
used, instead of polluting module scope with helpers nobody else calls.
No special naming needed — the enclosing scope already marks them as
private to that function.

## Naming (PEP 8)

- `snake_case` for functions, variables, modules.
- `PascalCase` for classes and exceptions.
- `UPPER_CASE` for module-level constants.
- Single leading underscore (`_name`) for "internal, not part of the
  public API" — not enforced by Python, just a signal to readers/tools.
- Avoid single-letter names except throwaway loop counters (`i`, `j`)
  or well-known math symbols.

## Line length & formatting

- 88 characters (the Black/Ruff default) rather than PEP 8's original
  79 — it's the de facto community standard now and what Ruff's
  formatter assumes out of the box.
- One statement per line; no semicolon-chained statements.

## Type hints (PEP 484 / 585 / 604)

- Type-hint public function signatures (params + return). Optional for
  short private/nested helpers where it doesn't add clarity.
- Built-in generics, not `typing` aliases: `list[str]`, `dict[str, int]`,
  not `List[str]`, `Dict[str, int]` (PEP 585, Python 3.9+).
- `X | None` instead of `Optional[X]` (PEP 604, Python 3.10+).
- Avoid `Any` unless the type genuinely can't be narrowed.

## Imports (PEP 8)

Group in this order, separated by a blank line, alphabetized within
each group:

1. Standard library
2. Third-party (`typer`, etc.)
3. Local (`pymedia.*`)

No wildcard imports (`from module import *`).

## Comparisons & booleans

- `is` / `is not` for `None`, `True`, `False` — never `==`.
- Don't compare booleans to literals: `if is_valid:` not
  `if is_valid == True:`.
- Truthiness over explicit length checks: `if items:` not
  `if len(items) > 0:`.

## Mutable defaults

Never use a mutable object (`list`, `dict`, `set`) as a default
argument — it's shared across calls. Use `None` and initialize inside:

```python
def process(items: list[str] | None = None) -> list[str]:
    items = items if items is not None else []
```

## Exceptions

- Never bare `except:` — catch specific exception types.
- Custom exceptions inherit from a project base (already the case here
  with `PyMediaError`), never bare `Exception` directly.
- Raise with context when wrapping: `raise Foo(...) from err`.

## f-strings

f-strings for interpolation (`f"{value}"`), not `%` or `.format()` —
standard since 3.6 and what Ruff/Black assume when auto-fixing.

## Context managers

Always `with` for anything with explicit cleanup (files, subprocesses,
locks) — never manual `open()`/`close()` pairs.

## `__all__` and module docstrings

- Module-level docstring at the top of any file meant to be imported
  from elsewhere (one line is enough if the module is small).
- `__all__` only where you're deliberately curating a public surface
  (e.g. a package `__init__.py`) — skip it in ordinary internal modules,
  it's noise there.

## Open questions / not yet decided

- Audio commands don't have parameters classes yet.
- Multi-language message templates: Typer help strings still pending.
