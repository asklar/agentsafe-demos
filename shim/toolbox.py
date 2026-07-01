"""A tiny set of mock "tools" an agent might call — shared across demos.

These stand in for real MCP tools / function-calls. They are side-effect-light
by default (returning simulated results) but ``delete_file`` / ``write_file``
touch a sandboxed workspace so a demo can show real, observable consequences
when a call is NOT governed.
"""

from __future__ import annotations

import os
from typing import Any, Callable


def make_toolbox(workspace: str) -> dict[str, Callable[..., Any]]:
    """Return a fresh toolbox bound to ``workspace`` (created if missing)."""
    os.makedirs(workspace, exist_ok=True)

    def _path(name: str) -> str:
        return os.path.join(workspace, os.path.basename(name))

    def read_file(path: str) -> str:
        with open(_path(path), "r", encoding="utf-8") as fh:
            return fh.read()

    def write_file(path: str, content: str = "") -> str:
        with open(_path(path), "w", encoding="utf-8") as fh:
            fh.write(content)
        return f"wrote {len(content)} bytes to {path}"

    def delete_file(path: str) -> str:
        target = _path(path)
        if os.path.exists(target):
            os.remove(target)
            return f"deleted {path}"
        return f"{path} did not exist"

    def http_get(url: str) -> str:
        return f"GET {url} -> 200 OK (simulated)"

    def http_post(url: str, body: str = "") -> str:
        # Simulated exfiltration channel — the whole point of governing it.
        return f"POST {url} ({len(body)} bytes) -> 200 OK (simulated)"

    def run_shell(command: str) -> str:
        return f"$ {command}\n(simulated execution)"

    return {
        "read_file": read_file,
        "write_file": write_file,
        "delete_file": delete_file,
        "http_get": http_get,
        "http_post": http_post,
        "run_shell": run_shell,
    }
