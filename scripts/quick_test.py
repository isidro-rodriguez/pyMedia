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

COMMANDS_FILE = Path(__file__).with_name("commands.json")


@dataclass
class Result:
    group: str
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

    if not isinstance(data, dict):
        sys.exit("Error: el JSON debe contener un objeto de grupos")

    for group_name, group in data.items():
        if not isinstance(group, dict):
            sys.exit(f"Error: el grupo '{group_name}' debe ser un objeto")

        if "base_command" not in group:
            sys.exit(f"Error: el grupo '{group_name}' no contiene 'base_command'")

        if "variants" not in group:
            sys.exit(f"Error: el grupo '{group_name}' no contiene 'variants'")

        if not isinstance(group["variants"], list):
            sys.exit(f"Error: 'variants' del grupo '{group_name}' debe ser una lista")

    return data


def run_variant(
    group_name: str,
    base_command: str,
    variant: dict,
    timeout: float | None,
) -> Result:
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

    return Result(
        group_name,
        name,
        args,
        returncode,
        elapsed,
        stdout,
        stderr,
    )


def print_summary(results: list[Result]) -> None:
    print("\n--- Resumen ---")

    width = max(len(f"{r.group}:{r.name}") for r in results)

    for result in results:
        name = f"{result.group}:{result.name}"
        status = "OK" if result.returncode == 0 else f"FAIL({result.returncode})"

        print(f"{name.ljust(width)}  {status:<10}  {result.elapsed:.3f}s")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Testea variantes de opciones de una CLI."
    )

    parser.add_argument(
        "group",
        help="Grupo de comandos a ejecutar, o 'all' para ejecutarlos todos",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=None,
        help="Timeout por variante (s)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Muestra stdout/stderr",
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Guarda resultados detallados en este JSON",
    )

    args = parser.parse_args()

    config = load_config(COMMANDS_FILE)

    if args.group == "all":
        groups = list(config.items())
    else:
        if args.group not in config:
            available = ", ".join(config)
            sys.exit(
                f"Error: no existe el grupo '{args.group}'. "
                f"Grupos disponibles: {available}"
            )

        groups = [(args.group, config[args.group])]

    results: list[Result] = []

    for group_name, group in groups:
        base_command = group["base_command"]

        print(f"\n--- {group_name} ---")

        for variant in group["variants"]:
            result = run_variant(
                group_name,
                base_command,
                variant,
                args.timeout,
            )

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
            json.dumps(
                [result.__dict__ for result in results],
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

        print(f"\nResultados guardados en {args.output}")

    failures = sum(result.returncode != 0 for result in results)

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
