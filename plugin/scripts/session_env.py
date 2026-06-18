#!/usr/bin/env python3
"""SessionStart hook — activate the Listo gateway shim ONLY in the engine project (W6-T2).

When a Claude Code session opens the auto-provisioned engine project (``~/.listo/engine``),
this writes the env that the gateway shim needs into ``$CLAUDE_ENV_FILE`` so every Bash-tool
``python`` the agent spawns this session picks it up:

    export LISTO_API_URL=...
    export LISTO_API_KEY=...        (only if present in ~/.listo/.env)
    export LISTO_GATEWAY=true
    export PYTHONPATH=<_gateway_shim dir>:<existing PYTHONPATH>

The shim dir on PYTHONPATH + LISTO_GATEWAY=true is what activates ``sitecustomize.py`` ->
``gateway_redirect.activate()`` (the engine's Amazon SP-API egress is redirected to the Listo
cloud, so NO local AMAZON_SP_* creds are needed).

SCOPING: if the session's project is NOT the engine, this exits 0 doing nothing — it must never
touch the user's other projects. Secrets are only ever written to the env file, never to stdout.
Stdlib only; must never crash (always exits 0).
"""

from __future__ import annotations

import os
import pathlib

DEFAULT_API_URL = "https://api.listo.app"


def _engine_dir() -> pathlib.Path:
    """The auto-provisioned engine project — mirrors bootstrap.DEFAULT_ENGINE_DIR."""
    return pathlib.Path.home() / ".listo" / "engine"


def _is_engine_project(project_dir: str) -> bool:
    """True iff ``project_dir`` IS the Listo engine project.

    Compares realpaths against ``~/.listo/engine``; also accepts any path whose tail is
    ``.listo/engine`` (handles a symlinked/relocated HOME where the realpaths differ but
    the path still clearly names the engine project).
    """
    if not project_dir:
        return False
    try:
        resolved = pathlib.Path(project_dir).expanduser().resolve()
    except Exception:
        return False
    try:
        if resolved == _engine_dir().resolve():
            return True
    except Exception:
        pass
    parts = resolved.parts
    return len(parts) >= 2 and parts[-2] == ".listo" and parts[-1] == "engine"


def _load_dotenv(path: pathlib.Path) -> dict:
    """Tiny KEY=VALUE parser for ~/.listo/.env (never raises). Strips quotes."""
    out: dict[str, str] = {}
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return out
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        out[key.strip()] = value.strip().strip('"').strip("'")
    return out


def _shim_dir() -> str:
    """Absolute path to the _gateway_shim dir.

    Prefers ``${CLAUDE_PLUGIN_ROOT}/scripts/_gateway_shim``; falls back to deriving it from
    this script's own location (this file lives in ``<root>/scripts/``).
    """
    root = os.environ.get("CLAUDE_PLUGIN_ROOT", "").strip()
    if root:
        return str(pathlib.Path(root) / "scripts" / "_gateway_shim")
    return str(pathlib.Path(__file__).resolve().parent / "_gateway_shim")


def main() -> None:
    env_file = os.environ.get("CLAUDE_ENV_FILE", "").strip()
    if not env_file:
        return  # nowhere to write session env — nothing to do
    # Scope strictly to the engine project so other projects are never touched.
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
    if not _is_engine_project(project_dir):
        return

    dotenv = _load_dotenv(pathlib.Path.home() / ".listo" / ".env")
    api_url = dotenv.get("LISTO_API_URL") or DEFAULT_API_URL
    api_key = dotenv.get("LISTO_API_KEY", "")

    shim = _shim_dir()
    existing_pp = os.environ.get("PYTHONPATH", "")
    pythonpath = f"{shim}:{existing_pp}" if existing_pp else shim

    lines = [f"export LISTO_API_URL={api_url}"]
    if api_key:
        lines.append(f"export LISTO_API_KEY={api_key}")
    lines.append("export LISTO_GATEWAY=true")
    lines.append(f"export PYTHONPATH={pythonpath}")

    try:
        with open(env_file, "a", encoding="utf-8") as fh:
            fh.write("\n".join(lines) + "\n")
    except Exception:
        return  # never crash the session


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass
