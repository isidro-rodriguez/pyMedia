# Agent Guidelines for Python Code Quality

## Core Principles

- Readable, straightforward code.
- Reuse well-known standard-library or lightweight third-party tools.
- Avoid unnecessary complexity.

## Code Style

- Follow PEP 8. 4-space indentation, snake_case for functions/vars, PascalCase for classes, UPPER_CASE for constants.
- Use f-strings for formatting.
- Use `is` for comparisons with `None`/`True`/`False`.
- Use list/generator comprehensions and `enumerate()` where they read better than the manual version.
- Skip comments that just restate the code. Comment on _why_, not _what_, when it's not obvious.
- Don't leave debug prints, commented-out code, or leak prompt/task context into comments.
- Use type hints on function signatures.

## Documentation

- Docstrings for all public functions/classes, google style (Args:, Returns:, Raises: sections).
- Short comments for private or anidated functions.

## Error Handling

- No bare `except:`. Catch specific exceptions.
- Don't silently swallow errors — at least a comment or log line.
- Use `with` for files and other resources.

## Function & Class Design

- Single responsibility, but don't split things into fragments to satisfy an abstract rule — some 15-line scripts are fine as one function.
- Never use mutable default arguments.
- Dataclasses for simple data containers.

## Testing

- Tests are welcome for logic worth protecting (parsers, calculators, anything with edge cases), not mandatory for glue/UI code.
- pytest if tests exist. Arrange-Act-Assert.

## Imports

- No wildcard imports.
- Standard library, then third-party, then local — roughly grouped is enough.

## Tools

- Ruff for formatting/linting is mandatory.
- `uv` is mandatory for package managing.

## Security

- No secrets/API keys hardcoded — use environment variables or a `.env` (gitignored).
- Don't log tokens, passwords, or PII.
