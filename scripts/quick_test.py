#!/usr/bin/env python3
"""Ejecuta y compara variantes de opciones de una aplicación CLI."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Result:
    name: str
    args: str
    returncode: int
    elapsed: float
    stdout: str
    stderr: str


def load_config(json_path: Path) -> dict:
    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        sys.exit(f"Error: no existe el fichero '{json_path}'")
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: JSON inválido en '{json_path}': {exc}")

    if "base_command" not in data or "variants" not in data:
        sys.exit("Error: el JSON debe tener 'base_command' y 'variants'")
    return data


def run_variant(base_command: str, variant: dict, timeout: float | None) -> Result:
    name = variant.get("name", "<sin nombre>")
    args = variant.get("args", "")
    full_cmd = shlex.split(base_command) + shlex.split(args)

    start = time.perf_counter()
    try:
        proc = subprocess.run(
            full_cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        returncode = proc.returncode
        stdout, stderr = proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        returncode = -1
        stdout, stderr = "", "TIMEOUT"
    except FileNotFoundError:
        returncode = -2
        stdout, stderr = "", f"Comando no encontrado: {full_cmd[0]}"
    elapsed = time.perf_counter() - start

    return Result(name, args, returncode, elapsed, stdout, stderr)


def print_summary(results: list[Result]) -> None:
    print("\n--- Resumen ---")
    width = max(len(r.name) for r in results)
    for r in results:
        status = "OK" if r.returncode == 0 else f"FAIL({r.returncode})"
        print(f"{r.name.ljust(width)}  {status:<10}  {r.elapsed:.3f}s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Testea variantes de opciones de una CLI."
    )
    parser.add_argument(
        "filename", help="Nombre base del fichero (sin extensión .json)"
    )
    parser.add_argument(
        "--timeout", type=float, default=None, help="Timeout por variante (s)"
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Muestra stdout/stderr"
    )
    parser.add_argument(
        "-o", "--output", help="Guarda resultados detallados en este JSON"
    )
    args = parser.parse_args()

    config = load_config(Path(f"./scripts/commands/{args.filename}.json"))
    base_command = config["base_command"]

    results = []
    for variant in config["variants"]:
        result = run_variant(base_command, variant, args.timeout)
        results.append(result)

        status = "OK" if result.returncode == 0 else "FAIL"
        print(f"[{status}] {result.name} ({result.args}) -> {result.elapsed:.3f}s")
        if args.verbose:
            if result.stdout:
                print(f"  stdout: {result.stdout.strip()}")
            if result.stderr:
                print(f"  stderr: {result.stderr.strip()}")

    print_summary(results)

    if args.output:
        Path(args.output).write_text(
            json.dumps([r.__dict__ for r in results], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"\nResultados guardados en {args.output}")

    failures = sum(1 for r in results if r.returncode != 0)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
