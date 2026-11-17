# AGENTS.md

Instructions for AI agents working on **pyMedia**: CLI sencilla para `ffmpeg`: analiza, corta, une, convierte y edita vídeo, audio y subtítulos.

The shared sections below are the same in every project. Project-specific rules are at the
end, under **Project rules**, and take precedence when they differ.

<!-- shared:start — managed by assistant-skills/new-python-project (scaffold.py sync). Edit there, not here. -->
## Shared rules

**Language.** Code and identifiers in English. Docstrings, comments, README, `docs/`,
CHANGELOG, commits and user-facing messages in Spanish. This file stays in English.

**Tools.** `uv` only, never `pip install`; run everything from the project root.
Quality gate: `uv run ruff format --check .`, `uv run ruff check .`, `uv run ty check`,
`uv run pytest`. The same gate as `poe check`, if Poe the Poet is installed globally; poe is
never a project dependency, and everything must also work with plain `uv run`.

**Workflow.**

1. Read `README.md`, `pyproject.toml`, this file and the related tests before changing code.
2. Make the smallest change that solves the task: no unrelated refactors, no formatting of
   untouched files, no new dependency without a reason (prefer the standard library).
3. Don't change CI, tool configuration or project structure unless the task needs it.
4. Don't run a failing command more than twice: stop, give the root cause and the exact error,
   propose the minimal fix and ask.
5. Don't run state-changing git commands (commit, push, tag, reset, rebase) unless the user
   asks or the commit policy in **Project rules** allows it. Never `--no-verify`.
6. Leave no secrets, temporary files or TODOs without context. Never hand-edit `uv.lock`.

**Code.** Strict type hints on every signature. Google-style docstrings: complete for public
identifiers, one line for private ones; a public docstring's `Raises` also lists the
exceptions raised by the private functions it calls. Comments explain the *why*. Prefer
simple, explicit code; `pathlib` over `os.path`. Ruff and ty enforce the rest; don't fight
them with ignores.

**Tests.** `pytest` in `tests/`. Cover relevant logic and every fixed bug; they must pass on
Linux and Windows.

**Commits.** Conventional Commits in Spanish (`feat:`, `fix:`, `docs:`, `test:`,
`refactor:`, `chore:`), one intent per commit, explaining the *why*.

**Releases.** Only for versioned projects (a real version and `CHANGELOG.md`). Before
pushing changes to the package, use the `python-release` skill. Without it: SemVer bump,
`## [Unreleased]` → `## [X.Y.Z] - YYYY-MM-DD` in `CHANGELOG.md`, `uv lock`, then
`chore: bump versión a X.Y.Z`. Never tag without confirmation.

**Done** when the quality gate and any extra gate in **Project rules** pass, and the README
and docs reflect any change in usage.

Project rules below take precedence over these. Shared rules change in assistant-skills
(`scaffold.py sync`), not by hand here.
<!-- shared:end -->

## Project rules

pyMedia is a Typer CLI that wraps `ffmpeg`/`ffprobe` for everyday media tasks. Read
`docs/desarrollo/arquitectura.md` before touching code. `ffmpeg` and `ffprobe` must be in
`PATH` to run the app and the end-to-end tests.

### Language: messages go through gettext

Overrides the shared rule for user-facing messages: they are gettext `msgid`s **in English**,
wrapped in `_()` (`from pymedia.locales import translate as _`), with the Spanish translation in
`src/pymedia/locales/spanish/LC_MESSAGES/pymedia.po`. Never hardcode Spanish in messages.
Build them at raise time with `_("msgid") % {...}`. When any `_()` text is added, edited or
removed:

```bash
uv run python scripts/i18n.py extract
uv run python scripts/i18n.py update -l spanish
# translate empty/fuzzy entries in pymedia.po
uv run python scripts/i18n.py compile -l spanish
uv run python scripts/i18n.py check
uv run pytest -m locales
```

### Structure

```
src/pymedia/
├── commands/<name>/  # one package per command: cli, parameters, cmd, service (+ base/)
├── mixins/           # reusable validation and ffmpeg fragments for parameters
├── models/           # dataclasses (Media, Video, Audio, Subtitles, Config…)
├── data/             # codec, container, format and language catalogs
├── locales/          # gettext catalogs (pymedia.pot, spanish/)
├── resources/        # default config.toml, icons, font, man page (pymedia.1)
├── ffprobe.py · errors.py · logger.py · theme.py · ui.py
├── __init__.py       # version = "X.Y.Z" (hatchling reads it; not in pyproject.toml)
└── main.py           # entry point (pymedia.main:run)
docs/                 # Zensical site, Spanish: usuario/, desarrollo/
scripts/              # build.py, package.py, i18n.py, generate_fixtures.py (+ fixtures/)
```

- Runtime dependencies are only `typer`, `rich` and `platformdirs`.
- `build/`, `site/` and `tests/fixtures/` (manual fixtures) are git-ignored.

### Architecture

Each command lives in `src/pymedia/commands/<name>/` with four layers. Copy a similar command
as a starting point (`docs/desarrollo/nuevo-comando.md`).

| Layer           | Responsibility |
|-----------------|----------------|
| `cli.py`        | Typer options (reuse `commands/base/cli_options.py`), reject impossible option combinations, `Logger.create`, load parameters, start the service. |
| `parameters.py` | Dataclass of `BaseParameters` + mixins; `load()` calls the mixins' `create_*` methods. |
| `cmd.py`        | Pure function returning the ffmpeg command as `list[str]`. No I/O, no logging. |
| `service.py`    | `BaseService` subclass: expected outputs, `resolve_overwrite`, `display_cmd`, `run_ffmpeg`, result message. |

- Reusable validation goes into a mixin (`create_*` validates, `to_*_cmd` returns ffmpeg args).
- Never add `-y`, `-n`, `-nostdin`, `-progress` or `-nostats` in `cmd.py`:
  `commands/base/ffmpeg_runner.py` (`prepare_command`) manages them.
- Always run ffmpeg through `BaseService.run_ffmpeg`, listing every output in `output_list`
  (outputs are staged in a temp dir and moved on success).
- Codec and container knowledge belongs in `src/pymedia/data/`, not in commands.
- All terminal output goes through `pymedia.ui.console` (via `Logger` or `logger.print`): never
  `print`, `rich.print` or a new `Console`. Use the named styles of `theme.py`, never raw
  colours. Ask with `pymedia.ui.confirm`, report finished operations with `logger.success`,
  pass help texts through `styled_help`.
- Register new commands in `main._build_app()` (imports stay inside the function).
- Raise exceptions from `errors.py`: `UserError` subclasses for user-fixable problems,
  `PyMediaError` subclasses for runtime/internal ones. Never silence errors; chain with
  `from err`.
- Keep functions around 20 lines.

### Tests

- The default run excludes the `binary` and `locales` markers. Never run `pytest -m binary`
  by hand: it builds the PyInstaller executable and only runs in CI.
- Visible behaviour fixes get a test in `tests/test_regressions.py`.
- Don't depend on the host OS: patch `os.name`/locale with `monkeypatch`.
- End-to-end tests use the `pymedia` fixture (runs each scenario in-process `[cli]` and against
  the binary `[binary]`); synthetic media come from `tests/conftest.py`, output inspection
  from `tests/helpers.py`.

### Extra quality gates

- Coverage ≥ 95 %: `uv run pytest --cov=pymedia --cov-fail-under=95` (CI and pre-push). Don't
  lower the threshold or weaken CI and hooks to make a change pass.
- `uv run pytest -m locales` when messages changed (CI and pre-push).
- Docs: if `docs/`, `zensical.toml` or `docs_templates/` changed, `uv run zensical build`
  must end with "No issues found". If commands or options changed, update `README.md`,
  `docs/` and the man page `src/pymedia/resources/pymedia.1`:
  `tests/test_docs_consistency.py` checks them against each other.
- Hooks (`uv run pre-commit install`): pre-commit runs ruff, ty and pytest; pre-push runs
  `uv lock --check`, coverage and locales. `poe ci` reproduces the CI quality job.
- CI (`.github/workflows/ci.yaml`): ubuntu + windows, Python 3.12 and 3.13, with ffmpeg; a
  separate job builds the executable and runs `pytest -m binary`.

### Commit policy

Never commit automatically: report the result and wait for confirmation.

### Releases and publishing

- The CHANGELOG uses the Spanish Keep a Changelog headings: `## [Sin publicar]` and
  `### Añadido`, `Cambiado`, `Corregido`, `Eliminado`, `Obsoleto`, `Seguridad`, `Interno`.
- MAJOR means a breaking change to the CLI: removed or renamed commands or options.
- Publishing: push an annotated tag `vX.Y.Z` matching `src/pymedia/__init__.py`.
  `.github/workflows/releases.yaml` builds the executables, packages a `.deb` (built on
  Ubuntu 22.04) and a `.zip` (Windows) with `scripts/package.py`, and creates the GitHub
  Release with the CHANGELOG section as notes; `tests/test_package.py` requires that section.
