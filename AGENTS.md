# AGENTS.md

pyMedia: Typer CLI that wraps `ffmpeg`/`ffprobe` for everyday media tasks. Read
`docs/desarrollo/arquitectura.md` before touching code.

## Language

- **Code and identifiers in English**: variables, functions, constants, classes, methods,
  parameters, modules, and tests.
- **Documentation in Spanish**: docstrings, comments, README, `docs/`, CHANGELOG, and commits.
- **User-facing messages** are gettext `msgid`s written in English and wrapped in `_()`
  (`from pymedia.locales import translate as _`). Their Spanish translation lives in
  `src/pymedia/locales/spanish/LC_MESSAGES/pymedia.po`. Never hardcode Spanish text in
  messages.
- Exception names and internal identifiers must be in English.
- This file, `AGENTS.md`, is written in English so the agent does not need to translate
  instructions.

## Project structure

```bash
.
├── .github/                # CI and release workflows (Linux + Windows), Dependabot
├── .pre-commit-config.yaml # Git hooks: pre-commit (ruff, ty, pytest) and pre-push (cov, locales, binary)
├── AGENTS.md               # This file
├── CHANGELOG.md            # Keep a Changelog (Spanish)
├── LICENSE                 # MIT
├── README.md               # Short user-facing introduction
├── docs/                   # Zensical sources of the docs website (Spanish)
│   ├── index.md            # Landing page
│   ├── usuario/            # User guide (commands, config, formats, troubleshooting)
│   ├── desarrollo/         # Developer guide (architecture, new command, contributing)
│   └── assets/             # pymedia.css (CLI palette), images, favicons
├── docs_templates/         # Zensical template overrides (favicons, manifest)
├── pyproject.toml          # Project: deps, build (hatchling), tools (ruff, ty, pytest)
├── scripts/                # build.py, package.py, i18n.py, generate_fixtures.py (+ fixtures/)
├── src/
│   └── pymedia/
│       ├── commands/       # One package per command: cli, parameters, cmd, service (+ base/)
│       ├── mixins/         # Reusable validation and ffmpeg fragments for parameters
│       ├── models/         # Dataclasses (Media, Video, Audio, Subtitles, Config…)
│       ├── data/           # Codec, container, format and language catalogs
│       ├── locales/        # gettext catalogs (pymedia.pot, spanish/)
│       ├── resources/      # Default config.toml, icons (executable), font, man page
│       ├── ffprobe.py      # ffprobe → models
│       ├── errors.py       # Localized exception hierarchy
│       ├── logger.py       # Rich console + rotating file logger
│       ├── theme.py        # UI palette and named styles
│       ├── ui.py           # Themed console, confirm, progress bar, Typer help theme
│       └── main.py         # Entry point (`pymedia.main:run`)
└── tests/                  # pytest suite (conftest generates synthetic media)
```

- Every `__init__.py` must include a short docstring describing the module or package.
- The project uses `uv` as dependency manager and `hatchling` as build backend.
- The package version lives in `src/pymedia/__init__.py` (`version = "..."`), not in
  `pyproject.toml`.
- `build/` and `tests/fixtures/` (manual fixtures) are git-ignored and must not be committed.

## Project rules (load-bearing)

- **One `uv.lock` and one venv** at the project root.
- **Use `uv sync`** (not `--all-packages`): resolves the current project and its `dev` group.
- **Run tools from the root** so they cover all code.
- Package dependencies go in `pyproject.toml` (`dependencies` and `dependency-groups.dev`).
- To add dependencies: `uv add <pkg>` (runtime) or `uv add --dev <pkg>` (dev).
- `ffmpeg` and `ffprobe` must be in `PATH` to run the app and the end-to-end tests.

## Tools and canonical commands

Do not use `pip install` directly. Run in this order and stop at the first failure:

```bash
uv sync
uv run ruff format .
uv run ruff check --fix .
uv run ruff check .
uv run ty check
uv run pytest
```

If user-facing messages changed (any `_()` text added, edited, or removed):

```bash
uv run python scripts/i18n.py extract
uv run python scripts/i18n.py update -l spanish
# translate empty/fuzzy entries in src/pymedia/locales/spanish/LC_MESSAGES/pymedia.po
uv run python scripts/i18n.py compile -l spanish
uv run python scripts/i18n.py check
uv run pytest -m locales
```

Do not run `uv run pytest -m binary` (slow, builds the PyInstaller binary): it only
runs in the `pre-push` hook and in CI, and passes whenever the regular suite does.

If `docs/`, `zensical.toml` or `docs_templates/` changed, the build must finish with
"No issues found" (broken links and anchors are reported as issues):

```bash
uv run zensical build        # output in site/ (git-ignored)
```

If a tool is missing, install it in the `dev` group:

```bash
uv add --dev <tool>
```

## Agent workflow

1. Before changing, read `README.md`, `pyproject.toml`, `AGENTS.md`, the relevant page in
   `docs/`, and related tests.
2. Make the smallest necessary change. Do not refactor unrelated code.
3. If you need a new dependency, justify it. If stdlib solves it, do not add it.
4. Do not modify CI, global config, or structure unless the task requires it.
5. Before finishing, run quality commands from the root and fix until they pass.
6. If something fails and you cannot resolve it, show the exact error and propose the
   minimal fix. Do not retry a failing command more than twice.
7. Do not leave secrets, temporary files, or TODOs without context.

## Architecture rules

Each command lives in `src/pymedia/commands/<name>/` with four layers. Copy an existing
similar command as template (`docs/desarrollo/nuevo-comando.md`).

| Layer           | Responsibility                                                         |
|-----------------|------------------------------------------------------------------------|
| `cli.py`        | Typer options (reuse `commands/base/cli_options.py`), reject impossible option combinations, `Logger.create`, load parameters, start service. |
| `parameters.py` | Dataclass composed of `BaseParameters` + mixins; `load()` calls the mixins' `create_*` methods. |
| `cmd.py`        | Pure function returning the ffmpeg command as `list[str]`. No I/O, no logging. |
| `service.py`    | `BaseService` subclass: expected outputs, `resolve_overwrite`, `display_cmd`, `run_ffmpeg`, result message. |

- Reusable validation goes into a mixin (`create_*` validates, `to_*_cmd` returns ffmpeg args).
- Never add `-y`, `-n`, `-nostdin`, `-progress` or `-nostats` in `cmd.py`:
  `ffmpeg_runner.prepare_command` manages them.
- Always run ffmpeg through `BaseService.run_ffmpeg`, listing every output in `output_list`
  (outputs are staged in a temp dir and moved on success).
- Codec/container knowledge belongs in `src/pymedia/data/`, not in commands.
- All terminal output goes through `pymedia.ui.console` (via `Logger` or `logger.print`).
  Never use `print`, `rich.print` or a new `Console`. Use named styles from
  `pymedia/theme.py`, never raw colors. Ask questions with `pymedia.ui.confirm`, report
  finished operations with `logger.success`, and pass help texts through `styled_help`.
- Register new commands in `main._build_app()` (imports stay inside the function).
- Raise the exceptions from `errors.py`: `UserError` subclasses for user-fixable problems,
  `PyMediaError` subclasses for runtime/internal ones. Build messages with
  `_("msgid") % {...}` at raise time. Never silence errors; chain with `from err`.

## Code rules

- Follow PEP 8 and Pythonic style with strict type annotations (checked by `ty`).
- Prefer the standard library; runtime dependencies are only `typer`, `rich` and
  `platformdirs`.
- Google-style docstrings for public identifiers: complete, with examples when they add value.
  Public docstrings inherit the `Raises` of the private functions they call.
- For private identifiers, use brief one-line docstrings.
- Do not repeat obvious things in docstrings or add unnecessary examples.
- Comments explain *why*, not *what*.
- Avoid overengineering. Prefer simple and explicit solutions.
- Keep functions (~20 lines) and classes small, with clear English names.
- No mutable default arguments. Imports ordered stdlib > third-party > local.

Example of a public docstring:

```python
def sum_numbers(a: int, b: int) -> int:
    """Suma dos números enteros.

    Args:
        a: Primer número.
        b: Segundo número.

    Returns:
        La suma de ``a`` y ``b``.

    Examples:
        >>> sum_numbers(2, 3)
        5
    """
    return a + b
```

## Tests

- Use `pytest`. Default run excludes the `binary` and `locales` markers.
- Cover relevant logic and fixed bugs (`tests/test_regressions.py` for visible behavior).
- Do not chase 100% coverage. Prioritize useful and readable tests.
- Tests must pass on Linux and Windows: patch `os.name`/locale with `monkeypatch`, never
  rely on the host.
- End-to-end tests use the `pymedia` fixture, which runs each scenario in-process
  (`[cli]`) and against the compiled binary (`[binary]`). Synthetic media come from
  `tests/conftest.py`; inspect outputs with `tests/helpers.py`.
- Test files live in `tests/`. Run `uv run pytest` from the root.

## CI

- GitHub Actions (`.github/workflows/ci.yml`) on `ubuntu-latest` and `windows-latest`,
  installing ffmpeg and `uv` (`astral-sh/setup-uv`), and running from the root:
    - `uv sync --locked`
    - `uv run ruff format --check .`
    - `uv run ruff check .`
    - `uv run ty check`
    - `uv run pytest --cov=pymedia --cov-fail-under=95` (Python 3.12 and 3.13)
    - `uv run pytest -m locales`
    - `uv run pytest -m binary` (separate job, uploads the executable)
- Dependabot (`.github/dependabot.yml`) updates `uv` dependencies and GitHub Actions weekly.
- Git hooks (`uv run pre-commit install`): `pre-commit` runs ruff, ty and pytest;
  `pre-push` runs pytest with coverage (≥ 95%), `-m locales` and `-m binary`.
- Do not weaken CI, hooks or the coverage threshold to make a change pass.

## Commits

- Never commit automatically; report success and wait for confirmation.
- Use Conventional Commits in Spanish.
- Examples:
    - `feat: añade comando clean para eliminar metadatos`
    - `fix: corrige validación de marcas de tiempo`
    - `docs: actualiza CHANGELOG para 0.22.0`
    - `test: cubre casos límite de --crop`
    - `chore: bump versión a 0.22.0`
- Atomic commit explaining the *why*, not just the *what*.
- Do not mix unrelated changes.

## Definition of done

A task is done when:

- `uv run ruff format --check .` passes without errors.
- `uv run ruff check .` passes without errors.
- `uv run ty check` passes without errors.
- `uv run pytest` passes without errors.
- If messages changed: catalogs updated and `uv run pytest -m locales` passes.
- `pytest -m binary` is left to the `pre-push` hook and CI; do not run it manually.
- `README.md` and `docs/` updated if commands, options, or usage change.
- `pymedia.1` updated too: `tests/test_docs_consistency.py` checks commands and options against README, `docs/` and the man page.
- `CHANGELOG.md` updated; version bumped before push.

## Versioning and changelog (pre-push)

Before any `git push` with code changes:

1. **Bump version** in `src/pymedia/__init__.py` following SemVer:
    - **MAJOR**: breaking changes to the CLI (removed/renamed commands or options).
    - **MINOR**: new backward-compatible functionality.
    - **PATCH**: bug fixes, internal refactors, docs.
2. **Update `CHANGELOG.md`** (Keep a Changelog, in Spanish):
    - Entries under `## [Sin publicar]` while working, or promote to
      `## [X.Y.Z] - YYYY-MM-DD` on bump.
    - Group under `### Añadido`, `### Cambiado`, `### Corregido`, `### Eliminado`,
      `### Obsoleto`, `### Seguridad`.
    - Write in Spanish, imperative or past tense, explaining the *why*.
3. **Lockfile consistency**: if the bump changes dependency constraints, update
   `pyproject.toml`, run `uv sync`, commit the updated `uv.lock`.
4. **Atomic release commit** before push:
    - `chore: bump versión a X.Y.Z`
    - `docs: actualiza CHANGELOG para X.Y.Z`
      Or a single combined commit if change and release are inseparable.

## Releases

- Publishing is done by pushing an annotated tag `vX.Y.Z` that matches
  `src/pymedia/__init__.py`. `.github/workflows/release.yml` builds the executables,
  packages a `.deb` (Linux, built on Ubuntu 22.04) and a `.zip` (Windows) with
  `scripts/package.py`, and creates the GitHub Release with the CHANGELOG section as notes.
- The CHANGELOG must have a `## [X.Y.Z]` section before tagging (tested in
  `tests/test_package.py`).
- Never create or push tags without explicit confirmation from the user.

If unsure whether a change is breaking, ask the user before choosing MAJOR. When in doubt
between PATCH and MINOR, prefer MINOR.

## Limits

- Do not modify `AGENTS.md` without justified reason.
- Do not use `pip install` directly.
- Do not add unnecessary dependencies.
- Do not change CI, Ruff, ty, pytest config without justification.
- Do not format files unrelated to the change.
- Do not rewrite code unnecessarily.
- If you cannot ask, choose the minimal change and document the assumption in the commit or PR.
