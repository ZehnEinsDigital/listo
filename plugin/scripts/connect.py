#!/usr/bin/env python3
"""/listo:connect helper — connect this device to a Listo account via the browser.

Opens the browser device-auth flow (like `gh login`): the user clicks Authorize and the key is
delivered + saved to ~/.listo/.env automatically. No key paste, no file editing.

LISTO_API_URL selects the cloud (defaults to the hosted cloud). It's read from the environment OR
from ~/.listo/.env — so a GUI user with no shell env can point at a local stack by putting a single
line `LISTO_API_URL=http://localhost:8000` in ~/.listo/.env first.

Advanced/CI (no browser): write `LISTO_API_KEY=lk_live_…` into ~/.listo/.env directly instead.
"""

from __future__ import annotations

import os
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import bootstrap  # noqa: E402  (after sys.path tweak so it works regardless of cwd)


def main() -> None:
    bootstrap.load_dotenv()  # pick up LISTO_API_URL from ~/.listo/.env (GUI has no shell env)
    api_url = (os.environ.get("LISTO_API_URL") or bootstrap.DEFAULT_API_URL).strip()
    dest = bootstrap.connect_via_browser(api_url)
    print(f"LISTO connected: saved to {dest}. Just describe what you want to list on Amazon.")


if __name__ == "__main__":
    main()
