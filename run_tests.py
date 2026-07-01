#!/usr/bin/env python3
"""run_tests.py — dependency-free test runner for the whole lab.

Discovers every test_*.py under shim/ and demos/, runs each `test_*` function,
and prints a summary. Uses only the stdlib so the lab stays install-free — but
the test files are also plain `pytest`-compatible if you prefer that.

Usage:  python3 run_tests.py
"""

from __future__ import annotations

import importlib.util
import os
import sys
import traceback

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)  # make `shim` importable everywhere


def _discover() -> list[str]:
    found = []
    for base in ("shim", "demos"):
        for dirpath, _dirs, files in os.walk(os.path.join(ROOT, base)):
            if "__pycache__" in dirpath or "_template" in dirpath:
                continue
            for name in files:
                if name.startswith("test_") and name.endswith(".py"):
                    found.append(os.path.join(dirpath, name))
    return sorted(found)


def _load(path: str):
    mod_name = "t_" + os.path.relpath(path, ROOT).replace(os.sep, "_")[:-3]
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def main() -> int:
    passed = failed = 0
    failures: list[tuple[str, str]] = []

    for path in _discover():
        rel = os.path.relpath(path, ROOT)
        try:
            mod = _load(path)
        except Exception:  # noqa: BLE001
            failed += 1
            failures.append((rel, traceback.format_exc()))
            print(f"LOAD FAIL  {rel}")
            continue

        for attr in sorted(dir(mod)):
            if not attr.startswith("test_"):
                continue
            fn = getattr(mod, attr)
            if not callable(fn):
                continue
            try:
                fn()
                passed += 1
                print(f"PASS  {rel}::{attr}")
            except Exception:  # noqa: BLE001
                failed += 1
                failures.append((f"{rel}::{attr}", traceback.format_exc()))
                print(f"FAIL  {rel}::{attr}")

    print("\n" + "=" * 48)
    print(f"{passed} passed, {failed} failed")
    for name, tb in failures:
        print("\n--- " + name + " ---")
        print(tb)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
